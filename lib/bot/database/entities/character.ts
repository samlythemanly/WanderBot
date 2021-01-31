import { DMChannel, NewsChannel, TextChannel } from 'discord.js';
import {
  Entity,
  PrimaryColumn,
  Column,
  ManyToOne,
  Repository,
  Equal,
} from 'typeorm';
import { User } from './user';

@Entity({ name: 'Characters' })
export class Character {
  @PrimaryColumn({ type: 'bigint' })
  id!: number;

  @ManyToOne(() => User, user => user.characters)
  owner!: User;

  @Column({ type: 'varchar', nullable: false })
  name!: string;

  @Column({ type: 'varchar', nullable: true })
  nickname!: string;

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

export const findCharacter = async (
  nameAndOwner: string,
  repository: Repository<Character>,
  channel: TextChannel | DMChannel | NewsChannel,
  shouldRejectExisting?: boolean
): Promise<Character> => {
  const characterNameAndOwner = nameAndOwner.split('|');

  const name = characterNameAndOwner[0];
  const owner = characterNameAndOwner[1];

  let character;

  if (owner) {
    character = await repository.findOne({
      where: [
        { name: Equal(name), owner: owner, isArchived: false },
        { nickname: Equal(name), owner: owner, isArchived: false },
      ],
      relations: ['owner'],
    });
  } else {
    character = await repository.findOne({
      where: [
        { name: Equal(name), isArchived: false },
        { nickname: Equal(name), isArchived: false },
      ],
      relations: ['owner'],
    });
  }

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
