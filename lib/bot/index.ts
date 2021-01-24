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
import { createTables } from './common/util';

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

  /**
   * Logs into the Discord bot and starts the activity manager.
   */
  async start(): Promise<void> {
    await this._database.initialize();
    this._characterRepository = this._database.connection.getRepository(
      Character
    );

    await this._client.login(discordBotId);

    this._scrapeActivityEveryThirtyMinutes();
  }

  /**
   * Runs the scrape method every thirty minutes, starting from the closest
   * thirty minute interval of the hour from now.
   *
   * i.e. If it's 1:15, it will wait until 1:30 to run, and then it will run
   * every 30 minutes thereafter.
   */
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

  /**
   * Sends an update to the admin of the bot containing information regarding
   * which characters are now on probation and which are now archived.
   */
  private async _sendMonthlyUpdate(): Promise<void> {
    const characters = await this._characterRepository.find({
      relations: ['owner'],
    });

    const charactersNowOnProbation = characters.filter(
      character => character.isOnProbation
    );
    const charactersNowArchived = characters.filter(
      character =>
        character.isArchived &&
        !this._archivedCharactersBeforeScrape.some(
          archivedCharacter => archivedCharacter.id === character.id
        )
    );
    const admin = await this._client.users.fetch(adminDiscordId);

    await admin.send(
      `Hello <@${admin.id}>! Happy ${new Date().toLocaleDateString('default', {
        month: 'long',
      })}. Here's your monthly update.`
    );

    if (charactersNowOnProbation.length === 0) {
      await admin.send('No characters were put on probation this month!');
    } else {
      await admin.send('These characters are now on probation:');

      const tables = createTables(
        'Characters now on probation',
        charactersNowArchived,
        ['name', 'owner', 'monthlyPostCount', 'postCount']
      );

      for (const table of tables) {
        await admin.send(table.toString());
      }
    }

    if (charactersNowArchived.length === 0) {
      await admin.send('No characters were archived this month!');
    } else {
      await admin.send('These characters are now archived:');

      const tables = createTables(
        'Characters now archived',
        charactersNowArchived,
        ['name', 'owner', 'monthlyPostCount', 'postCount']
      );

      for (const table of tables) {
        admin.send(`\`\`\`\n${table.toString()}\n\`\`\``);
      }
    }
  }
}

container.bind(Bot).toSelf().inSingletonScope();
