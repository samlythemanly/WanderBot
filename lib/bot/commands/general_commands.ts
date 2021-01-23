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
import { compliments, jokes, pluralize, Role } from '../common/constants';
import {
  Currency,
  formatConversion,
  getConversion,
  knutToGalleonRatio as galleonToKnutRatio,
  sickleToGalleonRatio as galleonToSickleRatio,
} from '../common/currency';
import { findUserWithName, User } from '../database/entities/user';
import { isStaffChannel } from './guards';
import { createTables } from '../common/util';

@Discord('!')
@injectable()
export abstract class GeneralCommands {
  @lazyInject(Database) private _database!: Database;
  private _users!: Repository<User>;

  @Once('ready')
  async initialize() {
    await this._database.initialize();
    this._users = this._database.connection.getRepository(User);
  }

  @Command('activity')
  @Infos({ usage: '!activity' })
  async activity(message: CommandMessage) {
    const user = await this._users.findOne(message.author.id, {
      relations: ['characters'],
    });

    if (!user) {
      message.channel.send(
        "Doesn't seem like you've been linked to a user yet, " +
          `${message.author}! Ask an admin to link your Discord account to a ` +
          'user.'
      );
      return;
    }

    message.author.send("Here's your current activity:\n");

    const characters = [
      ...user.characters.filter(character => !character.isArchived),
    ];

    const tables = createTables('Your current activity', characters, [
      'name',
      'monthlyPostCount',
      'postCount',
      'onProbation',
    ]);

    for (const table of tables) {
      message.channel.send(`\`\`\`\n${table.toString()}\n\`\`\``);
    }

    message.delete();
  }

  @Guard(isStaffChannel)
  @Command('activityFor :name')
  @Infos({ usage: '!activityFor <character name>' })
  async activityFor(message: CommandMessage) {
    const name = message.args.name;
    const user = await findUserWithName(name, this._users, message.channel);

    if (!user) return;

    message.channel.send(`Here's ${name}'s current activity:\n`);

    const characters = [
      ...user.characters.filter(character => !character.isArchived),
    ];

    const tables = createTables(`Activity for ${name}`, characters, [
      'name',
      'monthlyPostCount',
      'postCount',
      'onProbation',
    ]);

    for (const table of tables) {
      message.channel.send(`\`\`\`\n${table.toString()}\n\`\`\``);
    }
  }

  @Command('coinflip')
  @Infos({
    usage: '!coinflip',
  })
  coinflip(message: CommandMessage) {
    message.channel.send(
      Math.floor(Math.random() * 2) === 0 ? 'Heads!' : 'Tails!'
    );
  }

  @Command('compliment')
  @Infos({
    usage: '!compliment <user>',
  })
  compliment(message: CommandMessage) {
    const targetUser = message.mentions.users.first();

    if (!targetUser) {
      message.channel.send(
        "I don't know who you want me to compliment, so I'll compliment " +
          "myself. I'm a good bot and I do good things. Thanks " +
          `${message.author}!`
      );
    }

    const compliment =
      compliments[Math.floor(Math.random() * compliments.length)];
    message.channel.send(`Hey ${targetUser}, ${compliment}`);
  }

  @Command('convertMuggle :denomination :value')
  @Infos({
    usage: '!convertMuggle <denomination> <value>',
  })
  convertMuggle(message: CommandMessage) {
    if (message.args.value === undefined) return;
    const denomination = message.args.denomination
      .toString()
      .toLowerCase() as Currency;
    const value = Number.parseFloat(
      message.args.value.toString().replace(/[^0-9.]+/, '')
    );

    const conversion = getConversion(denomination);

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

    message.channel.send(
      `${formatConversion(
        conversion,
        value.toString()
      )} is approximately equal to ${galleons} ` +
        `${pluralize('galleon', galleons)}, ${sickles} ` +
        `${pluralize('sickle', sickles)}, and ${knuts} ` +
        `${pluralize('knut', knuts)}.`
    );
  }

  @Command('convertWix :denomination :galleons :sickles :knuts')
  @Infos({
    usage: '!convertWix <denomination> <galleons> <sickles> <knuts>',
  })
  convertWix(message: CommandMessage) {
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

    const conversion = getConversion(denomination);

    if (!conversion) {
      message.channel.send(
        `I'm sorry, we don't have a conversion rate for ${denomination}.`
      );
      return;
    }

    const converted = (
      (galleons + sickles / galleonToSickleRatio + knuts / galleonToKnutRatio) *
      conversion.galleonRatio
    ).toFixed(2);

    message.channel.send(
      `${galleons} ${pluralize('galleon', galleons)}, ${sickles} ` +
        `${pluralize('sickle', sickles)}, and ${knuts} ` +
        `${pluralize('knut', knuts)} is approximately equal to ` +
        `${formatConversion(conversion, converted)}.`
    );
  }

  @Command('help :command')
  @Infos({ isHidden: true, usage: 'hOw Do YoU uSe HeLp' })
  help(message: CommandMessage) {
    const isAdmin = message.guild?.roles.cache.has(Role.admin);
    const availableCommands = Client.getCommands().filter(command => {
      const isHidden = command.infos['isHidden'];
      if (isHidden) return false;
      if (isAdmin) return true;
      return !command.infos['isAdmin'];
    });

    const command = message.args.command;

    if (command) {
      const requestedCommand = availableCommands.find(
        cmd => cmd.commandName.toString() === command
      );
      if (!requestedCommand) {
        message.channel.send(`Sorry, I don't know what !${command} is!`);
        return;
      }

      message.channel.send(`!help\nUsage: ${requestedCommand.infos.usage}`);
      return;
    }

    message.channel.send(
      `Hi ${message.author}, you can run the following commands: ` +
        `${[
          ...new Set(
            availableCommands.map(command =>
              command.commandName.toString().replace(/(\w+)(.*)/, '$1')
            )
          ),
        ].join(', ')}.`
    );
  }

  @Command('halp')
  @Infos({ isHidden: true, usage: 'hOw Do YoU uSe HaLp' })
  halp(message: CommandMessage) {
    const isAdmin = message.guild?.roles.cache.has(Role.admin);
    const availableCommands = Client.getCommands().filter(command => {
      const isHidden = command.infos['isHidden'];
      if (!isHidden) return false;
      if (isAdmin) return true;
      return !command.infos['isAdmin'];
    });

    message.channel.send(
      `Surprise ${message.author}! You can run the following _*SPECIAL*_ ` +
        `commands: ${[
          ...new Set(
            availableCommands.map(command =>
              command.commandName.toString().replace(/(\w+)(.*)/, '$1')
            )
          ),
        ].join(', ')}.`
    );
  }

  @Command('joke')
  @Infos({ isHidden: true, usage: '!joke' })
  joke(message: CommandMessage) {
    const joke = jokes[Math.floor(Math.random() * jokes.length)];
    message.channel.send(joke[0]);
    setTimeout(() => message.channel.send(joke[1]), 3);
  }

  @Command('mock')
  @Infos({ isHidden: true, usage: '!mock <user>' })
  mock(message: CommandMessage) {
    const targetUser = message.mentions.users.first();

    if (!targetUser) {
      message.channel.send(
        "There's no one tagged to mock! Looks like the only fool here is you," +
          ` ${message.author}!`
      );
      return;
    }

    const lastMessage = message.channel.messages.cache
      .filter(message => message.author.id === targetUser.id)
      .last();

    if (!lastMessage) {
      message.channel.send(
        `${targetUser} hasn't sent a message in this channel!`
      );
      return;
    }

    const translatedMessage = [...lastMessage.content]
      .map((character, index) =>
        index % 2 === 0 ? character.toLowerCase() : character.toUpperCase()
      )
      .join('');

    message.channel.send(`"${translatedMessage}" - ${targetUser}`);
  }

  @Command('ping')
  @Infos({ usage: '!ping' })
  ping(message: CommandMessage) {
    message.channel.send('Pong!');
  }

  @CommandNotFound()
  commandNotFound(message: CommandMessage) {
    message.channel.send(
      "I'm sorry, I don't understand! Please type '!help' for a list of " +
        'commands I understand.'
    );
  }
}
