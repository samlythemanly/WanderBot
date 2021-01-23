import { DMChannel, NewsChannel, TextChannel } from 'discord.js';
import { Entity, Column, PrimaryColumn, OneToMany, Repository } from 'typeorm';
import { Character } from './character';

@Entity({ name: 'Users' })
export class User {
  @PrimaryColumn({ type: 'int' })
  discordId!: number;

  @Column({ type: 'varchar', nullable: false })
  name!: string;

  @OneToMany(() => Character, character => character.owner)
  characters!: Character[];
}

export const findUserWithName = async (
  name: string,
  repository: Repository<User>,
  channel: TextChannel | DMChannel | NewsChannel,
  shouldRejectExisting?: boolean
): Promise<User> => {
  const user = await repository.findOne(
    {
      name: name,
    },
    {
      relations: ['characters'],
    }
  );

  if (user && shouldRejectExisting) {
    channel.send(`User with name ${name} already exists!.`);
  }

  if (!user && !shouldRejectExisting) {
    channel.send(
      `Sorry, I couldn't find an existing user with the name ${name}.`
    );
  }

  return user;
};
