import { injectable } from 'inversify';
import { Connection, createConnection } from 'typeorm';
import container from '../config/inversify.config';

@injectable()
export class Database {
  public connection!: Connection;

  async initialize(): Promise<void> {
    if (this.connection) return;
    this.connection = await createConnection();
  }
}

container.bind(Database).toSelf().inSingletonScope();
