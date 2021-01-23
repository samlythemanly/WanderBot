// eslint-disable-next-line node/no-unpublished-import
import {
  Command,
  CommandMessage,
  Discord,
  Infos,
  Guard,
  Once,
  // eslint-disable-next-line node/no-unpublished-import
} from '@typeit/discord';
import { Repository } from 'typeorm';
import { Role, statuses } from '../common/constants';
import { Database } from '../database';
import {
  findCharacterWithName,
  Character,
} from '../database/entities/character';
import { findUserWithName, User } from '../database/entities/user';
import { hasRole } from './guards';
import { lazyInject } from '../config/inversify.config';
import { createTable } from '../common/util';

@Discord('!')
@Infos({ isAdmin: true })
export abstract class AdminCommands {
  @lazyInject(Database) private _database!: Database;
  private _users!: Repository<User>;
  private _characters!: Repository<Character>;

  @Once('ready')
  async initialize() {
    await this._database.initialize();
    this._characters = this._database.connection.getRepository(Character);
    this._users = this._database.connection.getRepository(User);
  }

  @Command('changeStatus')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!changeStatus',
  })
  changeStatus(message: CommandMessage) {
    const status = statuses[Math.floor(Math.random() * statuses.length)];

    message.client.user?.setActivity({ type: status[0], name: status[1] });
  }

  @Command('linkId :id :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!linkId <discord id> <alias>',
  })
  async linkDiscordId(message: CommandMessage) {
    const name = message.args.name;

    if (!name) {
      message.channel.send(
        "Sorry, I can't set your name to nothing. That would cause me to " +
          'explode.'
      );
      return;
    }

    const existingUserById = await this._users.findOne(
      message.args.id as number
    );

    if (existingUserById) {
      message.channel.send(
        `${existingUserById.name} is already linked to Discord ID ` +
          `${existingUserById.discordId}!`
      );
      return;
    }

    const existingUserByName = await findUserWithName(
      name,
      this._users,
      message.channel,
      true
    );

    if (existingUserByName) return;

    const user = new User();
    user.name = name;
    user.discordId = message.args.id;

    const newUser = await this._users.save(user);

    if (!newUser) {
      message.channel.send('Something went wrong in the linking process.');
      return;
    }

    message.channel.send(
      `${name} successfully linked to Discord ID ${newUser.discordId}!`
    );
  }

  @Command('linkCharacter :character :username')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!linkCharacter <character name> <user alias>',
  })
  async linkCharacter(message: CommandMessage) {
    const args = message.commandContent.split(' ').splice(1);
    const username = args.pop();
    const characterName = args.join(' ');

    const user = await findUserWithName(username, this._users, message.channel);

    if (!user) return;

    const character = await findCharacterWithName(
      characterName,
      this._characters,
      message.channel
    );
    if (!character) return;

    const result = await this._characters.update(character.id, { owner: user });

    if (!result.affected) {
      message.channel.send('Something went wrong linking.');
      return;
    }

    message.channel.send(
      `Successfully linked ${characterName} to ${username}.`
    );
  }

  @Command('unlinkCharacter :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!unlinkCharacter <character name>',
  })
  async unlinkCharacter(message: CommandMessage) {
    const name = message.commandContent.split(' ').splice(1).join(' ');

    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );

    if (!character) return;

    if (!character.owner) {
      message.channel.send(
        `${name} has already been orphaned and has no owner, are you trying ` +
          'to rub it in? You monster.'
      );
      return;
    }

    const result = await this._characters.update(character.id, { owner: null });

    if (!result.affected) {
      message.channel.send(`Something went wrong unlinking ${name}.`);
      return;
    }

    message.channel.send(
      `${name} successfully unlinked from ${character.owner.name}.`
    );
  }

  @Command('changeAlias :existing :new')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!changeAlias <existing alias> <new alias>',
  })
  async changeAlias(message: CommandMessage) {
    const existingName = message.args.existing;
    const newName = message.args.new;

    if (!newName) {
      message.channel.send(
        "Sorry, I can't change your name to nothing. That would cause me to " +
          'explode.'
      );
      return;
    }

    const existingUser = await findUserWithName(
      existingName,
      this._users,
      message.channel,
      true
    );

    if (existingUser) return;

    const userToUpdate = await findUserWithName(
      existingName,
      this._users,
      message.channel
    );
    if (!userToUpdate) return;

    const result = await this._users.update(userToUpdate, {
      name: message.args.new,
    });
    if (!result.affected) {
      message.channel.send(`Something went wrong changing names.`);
      return;
    }

    message.channel.send(
      `User's name successfully changed from ${existingName} to ${newName}!`
    );
  }

  @Command('unlinkDiscord :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!unlinkDiscord <alias>',
  })
  async unlinkDiscord(message: CommandMessage) {
    const name = message.args.name;

    const user = await findUserWithName(name, this._users, message.channel);

    if (!user) return;

    // Delete characters first, since if this fails but the Discord ID is
    // deleted some wonky behavior would occur.
    const characterWipeResult = await this._characters.update(
      user.characters.map(character => character.id),
      { owner: null }
    );

    if (!characterWipeResult.affected) {
      message.channel.send(`Something went wrong unlinking ${name}.`);
      return;
    }

    const discordIdDeletionResult = await this._users.delete(user.discordId);

    if (!discordIdDeletionResult.affected) {
      message.channel.send(`Something went wrong unlinking ${name}.`);
      return;
    }

    message.channel.send(
      `${name} successfully unlinked from Discord ID ${user.discordId}, and ` +
        `removed ${name} as the owner from all associated characters.`
    );
  }

  @Command('describe :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!describe <character name>',
  })
  async describe(message: CommandMessage) {
    const name = message.commandContent.split(' ').splice(1).join(' ');

    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );

    if (!character) {
      message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    const table = createTable(`Details for ${character.name}`, character, [
      'id',
      'name',
      'owner',
      'postCount',
      'totalPosts',
      'isNew',
      'isOnProbation',
      'isArchived',
    ]);

    message.channel.send(`\`\`\`\n${table.toString()}\n\`\`\``);
  }

  @Command('isArchived :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!isArchived <character name>',
  })
  async isArchived(message: CommandMessage) {
    const name = message.content.split(' ').slice(1).join(' ');

    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );

    if (!character) {
      message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    message.channel.send(
      `${name} is ${character.isArchived ? '' : ' NOT '} archived.`
    );
  }

  @Command('isOnProbation :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!isOnProbation <character name>',
  })
  async isOnProbation(message: CommandMessage) {
    const name = message.content.split(' ').slice(1).join(' ');

    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );

    if (!character) {
      message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    message.channel.send(
      `${name} is ${character.isOnProbation ? '' : ' NOT '} on probation.`
    );
  }

  @Command('setArchived :isArchived :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!setArchived <true/false/yes/no> <character name>',
  })
  async setArchived(message: CommandMessage) {
    const name = message.content.split(' ').slice(2).join(' ');
    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );
    const isArchived = this._parseBool(message.args.isArchived);

    if (!character) {
      message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    const result = await this._characters.update(character.id, {
      isArchived: ((isArchived ? 1 : 0) as unknown) as boolean,
    });

    if (!result.affected) {
      message.channel.send('Something went wrong.');
      return;
    }

    message.channel.send(`${name} is now ${isArchived ? '' : 'NOT '}archived.`);
  }

  @Command('setMonthlyPostCount :postCount :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!setMonthlyPostCount <post count> <character name>',
  })
  async setMonthlyPostCount(message: CommandMessage) {
    const name = message.content.split(' ').slice(2).join(' ');
    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );

    if (!character) {
      message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    const result = await this._characters.update(character.id, {
      monthlyPostCount: message.args.postCount,
    });

    if (!result.affected) {
      message.channel.send('Something went wrong.');
      return;
    }

    message.channel.send(
      `${name} now has a monthly post count of ${message.args.postCount}.`
    );
  }

  @Command('setProbation :isOnProbation :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!setProbation <true/false/yes/no> <character name>',
  })
  async setProbation(message: CommandMessage) {
    const name = message.content.split(' ').slice(2).join(' ');
    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );
    const isOnProbation = this._parseBool(message.args.isOnProbation);

    if (!character) {
      message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    const result = await this._characters.update(character.id, {
      isOnProbation: ((isOnProbation ? 1 : 0) as unknown) as boolean,
    });

    if (!result.affected) {
      message.channel.send('Something went wrong.');
      return;
    }

    message.channel.send(
      `${name} is now ${isOnProbation ? '' : 'NOT '}on probation.`
    );
  }

  @Command('setName :id :newName')
  @Guard(hasRole(Role.admin))
  @Infos({
    usage: '!setName <character id> <new character name>',
  })
  async setName(message: CommandMessage) {
    const id = message.args.id;
    const newName = message.content.split(' ').slice(2).join(' ');
    const character = await this._characters.findOne({ id: id });

    if (!character) {
      message.channel.send(`I couldn't find a character with ID ${id}.`);
      return;
    }

    const existingCharacter = await findCharacterWithName(
      newName,
      this._characters,
      message.channel,
      true
    );

    if (existingCharacter) return;

    const result = await this._characters.update(character.id, {
      name: newName,
    });

    if (!result.affected) {
      message.channel.send('Something went wrong.');
      return;
    }

    message.channel.send(
      `Successfully changed ${character.name}'s name to ${newName}.`
    );
  }

  private _parseBool(bool: string): boolean {
    const lowercase = bool.toLowerCase();
    return lowercase === 'yes' || lowercase === 'true';
  }
}
