import Axios from 'axios';
import * as cheerio from 'cheerio';
import { url } from '../common/constants';
import { injectable } from 'inversify';
import { Repository } from 'typeorm';
import { Database } from '../database';
import { Character } from '../database/entities/character';
import container, { lazyInject } from '../config/inversify.config';

@injectable()
export class ActivityManager {
  @lazyInject(Database) private _database: Database;
  private _charactersRepository: Repository<Character>;
  private _existingCharacters: Character[];
  private _updatedCharacters: Character[];
  private _newCharactersThisRun: Character[];

  axios = Axios.create();

  async _initialize() {
    await this._database.initialize();

    if (!this._charactersRepository) {
      this._charactersRepository = this._database.connection.getRepository(
        Character
      );
    }
  }

  private async _scrape(
    isFirstRunOfMonth: boolean,
    initialPageNumber?: number
  ): Promise<Character[]> {
    if (!initialPageNumber) initialPageNumber = 0;

    this._existingCharacters = await this._charactersRepository.find();

    const html = (await this.axios.get(url(initialPageNumber))).data;
    const createCheerio = cheerio.load(html);
    const rows = createCheerio('table > tr');

    for (const row of rows.toArray()) {
      const character = await this._processRow(createCheerio(row));
      character && this._updatedCharacters.push(character);
    }

    // The next page is 2 ahead because we have to account for the fact pages
    // in the site UI aren't indexed at 0 like the URL parameter is.
    const nextPage = `${initialPageNumber + 2}`;

    const pageNumber = createCheerio('.pagination_page').filter(
      (_, pageNumber) => createCheerio(pageNumber).text() === nextPage
    );

    if (pageNumber.text()) {
      return await this._scrape(isFirstRunOfMonth, initialPageNumber + 1);
    } else {
      if (isFirstRunOfMonth) this._updateProbationStatus();

      const result = await this._charactersRepository.save(
        this._updatedCharacters
      );

      console.log(`Updated ${result.length} characters.`);

      return result;
    }
  }

  private _updateProbationStatus() {
    const characters = [];
    for (const character of this._updatedCharacters) {
      if (!this._newCharactersThisRun.includes(character)) {
        if (character.monthlyPostCount < 2 && !character.isNew) {
          if (character.isOnProbation) {
            character.isOnProbation = false;
            character.isArchived = true;
          } else {
            character.isOnProbation = true;
          }
        }

        character.isNew = false;
      }

      character.monthlyPostCount = 0;
      characters.push(character);
    }
    this._updatedCharacters = characters;
  }

  private _extractCharacterId = (nameElement: cheerio.Cheerio): number => {
    const href = nameElement.find('a').attr('href');
    return parseInt(/.*showuser=(\d+).*/.exec(href)[1]);
  };

  private async _processRow(row: cheerio.Cheerio): Promise<Character> {
    const nameElement = row.find('.row4.name');

    if (!nameElement.text()) return null;

    const id = this._extractCharacterId(nameElement);
    const name = nameElement.text();
    const postCount = parseInt(row.find('.row4.posts').text());

    let character = this._existingCharacters.find(
      // eslint-disable-next-line eqeqeq
      character => character.id == id
    );
    if (!character) {
      character = new Character();
      character.id = id;
      character.name = name;
      character.isNew = true;
      character.isOnProbation = false;
      character.isArchived = false;

      this._charactersRepository.create(character);
      this._newCharactersThisRun.push(character);
    }

    // In case the character's name has changed.
    character.name = name;

    // Update the character's total and monthly post counts.
    character.monthlyPostCount =
      character.monthlyPostCount ?? 0 + (postCount - character.postCount ?? 0);
    character.postCount = postCount;

    if (character.monthlyPostCount >= 2) character.isOnProbation = false;

    return character;
  }

  async run(isFirstRunOfMonth: boolean): Promise<Character[]> {
    await this._initialize();

    this._existingCharacters = [];
    this._updatedCharacters = [];
    this._newCharactersThisRun = [];

    return await this._scrape(isFirstRunOfMonth);
  }
}

container.bind(ActivityManager).toSelf();
