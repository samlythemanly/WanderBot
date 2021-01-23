import { DMChannel, NewsChannel, TextChannel } from 'discord.js';
import { Entity, PrimaryColumn, Column, ManyToOne, Repository } from 'typeorm';
import { User } from './user';

@Entity({ name: 'Characters' })
export class Character {
  @PrimaryColumn({ type: 'int' })
  id!: number;

  @ManyToOne(() => User, user => user.characters)
  owner!: User;

  @Column({ type: 'varchar', nullable: false })
  name!: string;

  @Column({ type: 'int', nullable: false })
  postCount!: number;

  @Column({ type: 'int', nullable: false })
  monthlyPostCount!: number;

  @Column({ type: 'boolean', nullable: false })
  isOnProbation!: boolean;

  @Column({ type: 'boolean', nullable: false })
  isArchived!: boolean;

  @Column({ type: 'boolean', nullable: false })
  isNew!: boolean;
}

export const findCharacterWithName = async (
  name: string,
  repository: Repository<Character>,
  channel: TextChannel | DMChannel | NewsChannel,
  shouldRejectExisting?: boolean
): Promise<Character> => {
  const character = await repository.findOne(
    {
      name: name,
    },
    {
      relations: ['owner'],
    }
  );

  if (character && shouldRejectExisting) {
    channel.send(`A character named ${name} already exists!`);
  }

  if (!character && !shouldRejectExisting) {
    channel.send(
      `Sorry, I couldn't find an existing character with the name ${name}.`
    );
  }

  return character;
};
