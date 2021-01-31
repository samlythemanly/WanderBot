import { DMChannel, NewsChannel, TextChannel } from 'discord.js';
import {
  Entity,
  PrimaryColumn,
  Column,
  ManyToOne,
  Repository,
  Equal,
  WhereExpression,
  Like,
} from 'typeorm';
import { User } from './user';

@Entity({ name: 'Characters' })
export class Character {
  @PrimaryColumn({ type: 'bigint' })
  id!: number;

  @ManyToOne(() => User, user => user.characters, { eager: true })
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

  let character: Character;

  if (owner) {
    character = await repository
      .createQueryBuilder('character')
      .innerJoinAndSelect('character.owner', 'owner')
      .where('owner.name = :ownerName', { ownerName: owner })
      .andWhere('character.nickname = :nickname', { nickname: name })
      .orWhere('character.name = :characterName', { characterName: name })
      .getOne();
  } else {
    character = await repository.findOne({
      where: [{ name: Equal(name) }, { nickname: Equal(name) }],
      relations: ['owner'],
    });
  }

  if (character && shouldRejectExisting) {
    await channel.send(`A character named ${name} already exists!`);
  }

  if (!character && !shouldRejectExisting) {
    await channel.send(
      `Sorry, I couldn't find an existing character with the name ${name}.`
    );
  }

  return character;
};
