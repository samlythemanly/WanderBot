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
import { createTables } from '../common/util';

/**
 * Commands only admins have access to.
 */
@Discord('!')
export abstract class AdminCommands {
  @lazyInject(Database) private _database!: Database;
  private _users!: Repository<User>;
  private _characters!: Repository<Character>;

  /**
   * Initializes the database once the Discord bot emits a "ready" event.
   */
  @Once('ready')
  async initialize(): Promise<void> {
    await this._database.initialize();
    this._characters = this._database.connection.getRepository(Character);
    this._users = this._database.connection.getRepository(User);
  }

  /**
   * Changes the status of the discord bot to a random status defined in
   * the constants file.
   */
  @Command('changeStatus')
  @Guard(hasRole(Role.admin))
  @Infos({ isAdmin: true, isHidden: true, usage: '!changeStatus' })
  async changeStatus(message: CommandMessage): Promise<void> {
    const status = statuses[Math.floor(Math.random() * statuses.length)];

    await message.client.user?.setActivity({
      type: status[0],
      name: status[1],
    });
  }

  /**
   * Links a discord ID to an alias.
   */
  @Command('linkDiscord :id :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    isAdmin: true,
    isHidden: true,
    usage: '!linkDiscord <discord id> <alias>',
  })
  async linkDiscordId(message: CommandMessage): Promise<void> {
    const name = message.args.name;

    if (!name) {
      await message.channel.send(
        "Sorry, I can't set your name to nothing. That would cause me to " +
          'explode.'
      );
      return;
    }

    const existingUserById = await this._users.findOne(
      message.args.id as number
    );

    if (existingUserById) {
      await message.channel.send(
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
      await message.channel.send(
        'Something went wrong in the linking process.'
      );
      return;
    }

    await message.channel.send(
      `${name} successfully linked to Discord ID ${newUser.discordId}!`
    );
  }

  /**
   * Links a character name to a user alias.
   */
  @Command('linkCharacter :character :username')
  @Guard(hasRole(Role.admin))
  @Infos({
    isAdmin: true,
    isHidden: true,
    usage: '!linkCharacter <character name> <user alias>',
  })
  async linkCharacter(message: CommandMessage): Promise<void> {
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
      await message.channel.send('Something went wrong linking.');
      return;
    }

    await message.channel.send(
      `Successfully linked ${characterName} to ${username}.`
    );
  }

  /**
   * Unlinks a character name from a user alias.
   */
  @Command('unlinkCharacter :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    isAdmin: true,
    isHidden: true,
    usage: '!unlinkCharacter <character name>',
  })
  async unlinkCharacter(message: CommandMessage): Promise<void> {
    const name = message.commandContent.split(' ').splice(1).join(' ');

    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );

    if (!character) return;

    if (!character.owner) {
      await message.channel.send(
        `${name} has already been orphaned and has no owner, are you trying ` +
          'to rub it in? You monster.'
      );
      return;
    }

    const result = await this._characters.update(character.id, { owner: null });

    if (!result.affected) {
      await message.channel.send(`Something went wrong unlinking ${name}.`);
      return;
    }

    await message.channel.send(
      `${name} successfully unlinked from ${character.owner.name}.`
    );
  }

  /**
   * Changes a user's alias to a new one.
   */
  @Command('changeAlias :existing :new')
  @Guard(hasRole(Role.admin))
  @Infos({
    isAdmin: true,
    isHidden: true,
    usage: '!changeAlias <existing alias> <new alias>',
  })
  async changeAlias(message: CommandMessage): Promise<void> {
    const existingName = message.args.existing;
    const newName = message.args.new;

    if (!newName) {
      await message.channel.send(
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
      await message.channel.send(`Something went wrong changing names.`);
      return;
    }

    await message.channel.send(
      `User's name successfully changed from ${existingName} to ${newName}!`
    );
  }

  /**
   * Unlinks a discord ID from a user alias.
   */
  @Command('unlinkDiscord :name')
  @Guard(hasRole(Role.admin))
  @Infos({ isAdmin: true, isHidden: true, usage: '!unlinkDiscord <alias>' })
  async unlinkDiscord(message: CommandMessage): Promise<void> {
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
      await message.channel.send(`Something went wrong unlinking ${name}.`);
      return;
    }

    const discordIdDeletionResult = await this._users.delete(user.discordId);

    if (!discordIdDeletionResult.affected) {
      await message.channel.send(`Something went wrong unlinking ${name}.`);
      return;
    }

    await message.channel.send(
      `${name} successfully unlinked from Discord ID ${user.discordId}, and ` +
        `removed ${name} as the owner from all associated characters.`
    );
  }

  /**
   * Describes a character by printing all of the character's information into
   * a table.
   */
  @Command('describe :name')
  @Guard(hasRole(Role.admin))
  @Infos({ isAdmin: true, isHidden: true, usage: '!describe <character name>' })
  async describe(message: CommandMessage): Promise<void> {
    const name = message.commandContent.split(' ').splice(1).join(' ');

    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );

    if (!character) {
      await message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    const table = createTables(
      `Details for ${character.name}`,
      [character],
      [
        'id',
        'name',
        'owner',
        'monthlyPostCount',
        'postCount',
        'isNew',
        'isOnProbation',
        'isArchived',
      ],
      false
    );

    await message.channel.send(`\`\`\`\n${table.toString()}\n\`\`\``);
  }

  /**
   * Returns whether the provided character is archived.
   */
  @Command('isArchived :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    isAdmin: true,
    isHidden: true,
    usage: '!isArchived <character name>',
  })
  async isArchived(message: CommandMessage): Promise<void> {
    const name = message.content.split(' ').slice(1).join(' ');

    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );

    if (!character) {
      await message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    await message.channel.send(
      `${name} is ${character.isArchived ? '' : ' NOT '} archived.`
    );
  }

  /**
   * Returns whether the provided character is on probation.
   */
  @Command('isOnProbation :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    isAdmin: true,
    isHidden: true,
    usage: '!isOnProbation <character name>',
  })
  async isOnProbation(message: CommandMessage): Promise<void> {
    const name = message.content.split(' ').slice(1).join(' ');

    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );

    if (!character) {
      await message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    await message.channel.send(
      `${name} is ${character.isOnProbation ? '' : ' NOT '} on probation.`
    );
  }

  /**
   * Sets whether a character is archived.
   */
  @Command('setArchived :isArchived :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    isAdmin: true,
    isHidden: true,
    usage: '!setArchived <true/false/yes/no> <character name>',
  })
  async setArchived(message: CommandMessage): Promise<void> {
    const name = message.content.split(' ').slice(2).join(' ');
    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );
    const isArchived = this._parseBool(message.args.isArchived);

    if (!character) {
      await message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    const result = await this._characters.update(character.id, {
      isArchived: ((isArchived ? 1 : 0) as unknown) as boolean,
    });

    if (!result.affected) {
      await message.channel.send('Something went wrong.');
      return;
    }

    await message.channel.send(
      `${name} is now ${isArchived ? '' : 'NOT '}archived.`
    );
  }

  /**
   * Sets a new monthly post count for the provided character.
   */
  @Command('setMonthlyPostCount :postCount :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    isAdmin: true,
    isHidden: true,
    usage: '!setMonthlyPostCount <post count> <character name>',
  })
  async setMonthlyPostCount(message: CommandMessage): Promise<void> {
    const name = message.content.split(' ').slice(2).join(' ');
    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );

    if (!character) {
      await message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    const result = await this._characters.update(character.id, {
      monthlyPostCount: message.args.postCount,
    });

    if (!result.affected) {
      await message.channel.send('Something went wrong.');
      return;
    }

    await message.channel.send(
      `${name} now has a monthly post count of ${message.args.postCount}.`
    );
  }

  /**
   * Sets whether the provided character is on probation.
   */
  @Command('setProbation :isOnProbation :name')
  @Guard(hasRole(Role.admin))
  @Infos({
    isAdmin: true,
    isHidden: true,
    usage: '!setProbation <true/false/yes/no> <character name>',
  })
  async setProbation(message: CommandMessage): Promise<void> {
    const name = message.content.split(' ').slice(2).join(' ');
    const character = await findCharacterWithName(
      name,
      this._characters,
      message.channel
    );
    const isOnProbation = this._parseBool(message.args.isOnProbation);

    if (!character) {
      await message.channel.send(`I couldn't find a character named ${name}.`);
      return;
    }

    const result = await this._characters.update(character.id, {
      isOnProbation: ((isOnProbation ? 1 : 0) as unknown) as boolean,
    });

    if (!result.affected) {
      await message.channel.send('Something went wrong.');
      return;
    }

    await message.channel.send(
      `${name} is now ${isOnProbation ? '' : 'NOT '}on probation.`
    );
  }

  /**
   * Sets a new name for the provided character ID.
   *
   * This is the only place an admin ever has to reference a character ID. This
   * is the way it is because since Discord commands are all just strings with
   * arguments separated by spaces, it's impossible to tell for multi-word
   * arguments where one argument or another begins or ends. We could set up
   * some sort of delimiter in order to determine that, but character names
   * should never change that often, and it isn't hard to find the ID of a
   * character.
   */
  @Command('setName :id :newName')
  @Guard(hasRole(Role.admin))
  @Infos({
    isAdmin: true,
    isHidden: true,
    usage: '!setName <character id> <new character name>',
  })
  async setName(message: CommandMessage): Promise<void> {
    const id = message.args.id;
    const newName = message.content.split(' ').slice(2).join(' ');
    const character = await this._characters.findOne({ id: id });

    if (!character) {
      await message.channel.send(`I couldn't find a character with ID ${id}.`);
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
      await message.channel.send('Something went wrong.');
      return;
    }

    await message.channel.send(
      `Successfully changed ${character.name}'s name to ${newName}.`
    );
  }

  private _parseBool(bool: string): boolean {
    const lowercase = bool.toLowerCase();
    return lowercase === 'yes' || lowercase === 'true';
  }
}
