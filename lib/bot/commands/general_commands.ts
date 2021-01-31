// eslint-disable-next-line node/no-unpublished-import
import {
  Command,
  CommandMessage,
  Client,
  Discord,
  Infos,
  Once,
  Guard,
  CommandNotFound,
  // eslint-disable-next-line node/no-unpublished-import
} from '@typeit/discord';
import { injectable } from 'inversify';
import { Repository } from 'typeorm';
import { Database } from '../database';
import { lazyInject } from '../config/inversify.config';
import {
  compliments,
  jokes,
  attemptPluralization,
  Role,
} from '../common/constants';
import {
  conversions,
  Currency,
  formatConversion,
  knutToGalleonRatio as galleonToKnutRatio,
  sickleToGalleonRatio as galleonToSickleRatio,
} from '../common/currency';
import { findUserWithName, User } from '../database/entities/user';
import { isStaffChannel } from './guards';
import { createTables } from '../common/util';

/**
 * General commands available to everybody.
 */
@Discord('!')
@injectable()
export abstract class GeneralCommands {
  @lazyInject(Database) private _database!: Database;
  private _users!: Repository<User>;

  /**
   * Initializes the database once the Discord bot emits a "ready" event.
   */
  @Once('ready')
  async initialize(): Promise<void> {
    await this._database.initialize();
    this._users = this._database.connection.getRepository(User);
  }

  /**
   * Sends a DM to the calling user a table which contains the history
   * information for all of their active characters.
   */
  @Command('activity')
  @Infos({ usage: '!activity' })
  async activity(message: CommandMessage): Promise<void> {
    const user = await this._users.findOne(message.author.id, {
      relations: ['characters'],
    });

    if (!user) {
      await message.channel.send(
        "Doesn't seem like you've been linked to a user yet, " +
          `<@${message.author.id}>! Ask an admin to link your Discord account to a ` +
          'user.'
      );
      return;
    }

    await message.author.send("Here's your current activity:\n");

    const characters = [
      ...user.characters.filter(character => !character.isArchived),
    ];

    const tables = createTables('Your current activity', characters, [
      'name',
      'nickname',
      'monthlyPostCount',
      'postCount',
      'probationStatus',
    ]);

    for (const table of tables) {
      await message.author.send(`\`\`\`\n${table.toString()}\n\`\`\``);
    }

    await message.delete();
  }

  /**
   * Returns the activity for the provided user.
   */
  @Guard(isStaffChannel)
  @Command('activityFor :name')
  @Infos({ usage: '!activityFor <user name>' })
  async activityFor(message: CommandMessage) {
    const name = message.args.name;
    const user = await findUserWithName(name, this._users, message.channel);

    if (!user) return;

    message.channel.send(`Here's ${name}'s current activity:\n`);

    const characters = [
      ...user.characters.filter(character => !character.isArchived),
    ];

    const tables = createTables(`Activity for ${user.name}`, characters, [
      'name',
      'nickname',
      'monthlyPostCount',
      'postCount',
      'probationStatus',
    ]);

    for (const table of tables) {
      message.channel.send(`\`\`\`\n${table.toString()}\n\`\`\``);
    }
  }

  /**
   * Returns heads or tails; this doesn't need much explaining.
   */
  @Command('coinflip')
  @Infos({
    usage: '!coinflip',
  })
  async coinflip(message: CommandMessage): Promise<void> {
    await message.channel.send(
      Math.floor(Math.random() * 2) === 0 ? 'Heads!' : 'Tails!'
    );
  }

  /**
   * Returns a random compliment defined in the constants file, mentioning the
   * provided user.
   */
  @Command('compliment')
  @Infos({
    usage: '!compliment <user>',
  })
  async compliment(message: CommandMessage): Promise<void> {
    const targetUser = message.mentions.users.first();

    if (!targetUser) {
      await message.channel.send(
        "I don't know who you want me to compliment, so I'll compliment " +
          "myself. I'm a good bot and I do good things. Thanks " +
          `<@${message.author.id}>!`
      );
      return;
    }

    const compliment =
      compliments[Math.floor(Math.random() * compliments.length)];
    await message.channel.send(`Hey <@${targetUser.id}>, ${compliment}`);
  }

  /**
   * Converts the provided denomination and value of muggle money to the
   * equivalent value in galleons, sickles, and knuts.
   */
  @Command('convertMuggle :denomination :value')
  @Infos({
    usage: '!convertMuggle <denomination> <value>',
  })
  async convertMuggle(message: CommandMessage): Promise<void> {
    if (message.args.value === undefined) return;
    const denomination = message.args.denomination
      .toString()
      .toLowerCase() as Currency;
    const value = Number.parseFloat(
      message.args.value.toString().replace(/[^0-9.]+/, '')
    );

    const conversion = conversions.get(denomination);

    if (!conversion) {
      message.channel.send(
        `I'm sorry, we don't have a conversion rate for ${denomination}.`
      );
      return;
    }

    const converted = value / conversion.galleonRatio;
    const galleons = Math.floor(converted);
    const sickles = Math.floor((converted - galleons) * galleonToSickleRatio);
    const knuts = Math.floor(
      (converted - galleons - sickles / galleonToSickleRatio) *
        galleonToKnutRatio
    );

    await message.channel.send(
      `${formatConversion(
        conversion,
        value.toString()
      )} is approximately equal to ${galleons} ` +
        `${attemptPluralization('galleon', galleons)}, ${sickles} ` +
        `${attemptPluralization('sickle', sickles)}, and ${knuts} ` +
        `${attemptPluralization('knut', knuts)}.`
    );
  }

  /**
   * Converts the provided value in galleons, sickles, and nuts to the
   * equivalent value in muggle money of the provided denomination.
   */
  @Command('convertWix :denomination :galleons :sickles :knuts')
  @Infos({
    usage: '!convertWix <denomination> <galleons> <sickles> <knuts>',
  })
  async convertWix(message: CommandMessage): Promise<void> {
    if (
      message.args.galleons === undefined ||
      message.args.sickles === undefined ||
      message.args.knuts === undefined
    ) {
      return;
    }

    const denomination = message.args.denomination
      .toString()
      .toLowerCase() as Currency;

    const galleons = message.args.galleons;
    const sickles = message.args.sickles;
    const knuts = message.args.knuts;

    const conversion = conversions.get(denomination);

    if (!conversion) {
      await message.channel.send(
        `I'm sorry, we don't have a conversion rate for ${denomination}.`
      );
      return;
    }

    const converted = (
      (galleons + sickles / galleonToSickleRatio + knuts / galleonToKnutRatio) *
      conversion.galleonRatio
    ).toFixed(2);

    await message.channel.send(
      `${galleons} ${attemptPluralization('galleon', galleons)}, ${sickles} ` +
        `${attemptPluralization('sickle', sickles)}, and ${knuts} ` +
        `${attemptPluralization('knut', knuts)} is approximately equal to ` +
        `${formatConversion(conversion, converted)}.`
    );
  }

  /**
   * Returns a list of commands the user is able to execute, or returns the
   * usage of a command if one is provided and the user is permitted to send it.
   */
  @Command('help :command')
  @Infos({ isHidden: true, usage: 'hOw Do YoU uSe HeLp' })
  async help(message: CommandMessage): Promise<void> {
    const roles = message.member.roles.cache;
    const isAdmin =
      roles.some(role => role.name === Role.admin.toString()) ||
      roles.some(role => role.name === Role.wanderbotsFriend.toString());
    const allCommands = Client.getCommands().filter(command => {
      if (isAdmin) return true;
      return !command.infos['isAdmin'];
    });

    const availableCommands = allCommands.filter(
      command => !command.infos['isHidden']
    );

    const command = message.args.command;

    if (command) {
      const requestedCommand = allCommands.find(
        cmd => cmd.commandName.toString().split(' ')[0] === command
      );
      if (!requestedCommand) {
        await message.channel.send(`Sorry, I don't know what !${command} is!`);
        return;
      }

      await message.channel.send(
        `${command} usage: ${requestedCommand.infos.usage}`
      );
      return;
    }

    await message.channel.send(
      `Hi <@${message.author.id}>, you can run the following commands: ` +
        `${[
          ...new Set(
            availableCommands.map(command =>
              command.commandName.toString().replace(/(\w+)(.*)/, '$1')
            )
          ),
        ].join(', ')}.`
    );
  }

  /**
   * Returns a list of hidden commands the user is able to perform.
   */
  @Command('halp')
  @Infos({ isHidden: true, usage: 'hOw Do YoU uSe HaLp' })
  async halp(message: CommandMessage): Promise<void> {
    const roles = message.member.roles.cache;
    const isAdmin =
      roles.some(role => role.name === Role.admin.toString()) ||
      roles.some(role => role.name === Role.wanderbotsFriend.toString());
    const availableCommands = Client.getCommands().filter(command => {
      const isHidden = command.infos['isHidden'];
      if (!isHidden) return false;
      if (isAdmin) return true;
      return !command.infos['isAdmin'];
    });

    await message.channel.send(
      `Surprise <@${message.author.id}>! You can run the following ` +
        `_*SPECIAL*_ commands: ${[
          ...new Set(
            availableCommands.map(command =>
              command.commandName.toString().replace(/(\w+)(.*)/, '$1')
            )
          ),
        ].join(', ')}.`
    );
  }

  /**
   * Returns a random joke defined in the constants file.
   */
  @Command('joke')
  @Infos({ isHidden: true, usage: '!joke' })
  async joke(message: CommandMessage): Promise<void> {
    const joke = jokes[Math.floor(Math.random() * jokes.length)];
    await message.channel.send(joke[0]);
    setTimeout(async () => await message.channel.send(joke[1]), 3);
  }

  /**
   * Returns the last message from the target user, converted into spongebob-
   * mock-speak.
   */
  @Command('mock')
  @Infos({ isHidden: true, usage: '!mock <user>' })
  async mock(message: CommandMessage): Promise<void> {
    const targetUser = message.mentions.users.first();

    if (!targetUser) {
      await message.channel.send(
        "There's no one tagged to mock! Looks like the only fool here is you," +
          ` <@${message.author.id}>!`
      );
      return;
    }

    const lastMessage = message.channel.messages.cache
      .filter(message => message.author.id === targetUser.id)
      .last();

    if (!lastMessage) {
      await message.channel.send(
        `<@${targetUser.id}> hasn't sent a message in this channel!`
      );
      return;
    }

    const translatedMessage = [...lastMessage.content]
      .map((character, index) =>
        index % 2 === 0 ? character.toLowerCase() : character.toUpperCase()
      )
      .join('');

    await message.channel.send(`"${translatedMessage}" - <@${targetUser.id}>`);
  }

  /**
   * Returns "Pong!".
   *
   * Basically determines whether the bot is running properly.
   */
  @Command('ping')
  @Infos({ usage: '!ping' })
  async ping(message: CommandMessage): Promise<void> {
    await message.channel.send('Pong!');
  }

  /**
   * Sends a message to the channel when a command is executed that isn't
   * defined.
   */
  @CommandNotFound()
  async commandNotFound(message: CommandMessage): Promise<void> {
    await message.channel.send(
      "I'm sorry, I don't understand! Please type '!help' for a list of " +
        'commands I understand.'
    );
  }
}
