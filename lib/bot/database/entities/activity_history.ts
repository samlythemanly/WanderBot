import { Entity, PrimaryColumn, Column } from 'typeorm';

@Entity('NewActivityHistory')
export class ActivityHistory {
  @PrimaryColumn({ type: 'int' })
  characterId!: number;

  @Column({ type: 'int', nullable: false })
  monthlyPostCount!: number;

  @Column({ type: 'int', nullable: false })
  totalPostCount!: number;

  @Column({ type: 'timestamp', nullable: false })
  lastUpdated!: number;
}
