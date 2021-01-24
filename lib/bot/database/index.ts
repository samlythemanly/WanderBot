import { injectable } from 'inversify';
import { Connection, createConnection } from 'typeorm';
import container from '../config/inversify.config';

/**
 * Database containing all Discord user information as well as activity history
 * for characters.
 */
@injectable()
export class Database {
  public connection!: Connection;

  /**
   * Initializes the database's connection to the mysql server.
   */
  async initialize(): Promise<void> {
    if (this.connection) return;
    this.connection = await createConnection();
  }
}

container.bind(Database).toSelf().inSingletonScope();
