// eslint-disable-next-line node/no-unpublished-import
import { Client } from '@typeit/discord';
import { injectable } from 'inversify';
import { GeneralCommands } from './commands/general_commands';
import container, { lazyInject } from './config/inversify.config';
import { AdminCommands } from './commands/admin_commands';
import { ActivityManager } from './activity_manager';
import { Character } from './database/entities/character';
import { Database } from './database';
import { Repository } from 'typeorm';
import * as moment from 'moment';
import { adminDiscordId, discordBotId } from './config/private';

@injectable()
export class Bot {
  private _client: Client;

  @lazyInject(ActivityManager)
  private _activityManager: ActivityManager;

  @lazyInject(Database) private _database: Database;

  private _characterRepository: Repository<Character>;
  private _archivedCharactersBeforeScrape: Character[];

  constructor() {
    this._client = new Client({
      classes: [AdminCommands, GeneralCommands],
      silent: false,
      variablesChar: ':',
    });
  }

  async start(): Promise<void> {
    await this._database.initialize();
    this._characterRepository = this._database.connection.getRepository(
      Character
    );

    await this._client.login(discordBotId);

    this._scrapeActivityEveryThirtyMinutes();
  }

  private async _scrapeActivityEveryThirtyMinutes(): Promise<void> {
    const now = new Date();

    const nowMoment = moment(now);

    const nextRun = nowMoment.clone().add(30 - (nowMoment.minute() % 30), 'm');
    const timeUntilNextRun = nextRun.diff(nowMoment, 'ms', true);

    setTimeout(async () => {
      this._archivedCharactersBeforeScrape = await this._characterRepository.find(
        { isArchived: true }
      );
      const isFirstRunOfMonth = nextRun.day() === 1 && nextRun.hour() === 0;
      await this._activityManager.run(isFirstRunOfMonth);
      if (isFirstRunOfMonth) {
        await this._sendMonthlyUpdate();
      }

      // Wait 25 minutes before starting the next run.
      // This isn't 30 since the previous scrape won't have happened
      // instantaneously. We could _probably_ do 28 but *future proofing* ;)
      setTimeout(() => {
        this._scrapeActivityEveryThirtyMinutes();
      }, moment.duration(25, 'm').asMilliseconds());
    }, timeUntilNextRun);
  }

  private async _sendMonthlyUpdate() {
    const characters = await this._characterRepository.find();

    const charactersNowOnProbation = characters
      .filter(character => character.isOnProbation)
      .map(character => character.name);

    const charactersNowArchived = characters
      .filter(
        character =>
          character.isArchived &&
          !this._archivedCharactersBeforeScrape.some(
            archivedCharacter => archivedCharacter.id === character.id
          )
      )
      .map(character => character.name);

    const admin = await this._client.users.fetch(adminDiscordId);

    await admin.send(
      `Hello! Happy ${new Date().toLocaleDateString('default', {
        month: 'long',
      })}. Here's your monthly update.`
    );

    if (charactersNowOnProbation.length === 0) {
    } else {
      await admin.send(
        `These characters are now on probation: ${charactersNowOnProbation.join(
          ', '
        )}`
      );
    }

    if (charactersNowArchived.length === 0) {
      await admin.send('No characters were archived this month!');
    } else {
      await admin.send(
        `These characters are now archived: ${charactersNowArchived.join(', ')}`
      );
    }
  }
}

container.bind(Bot).toSelf().inSingletonScope();
