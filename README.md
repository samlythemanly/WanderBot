# Wanderbot - The Discord bot for Wander RP


## Steps to run this project:
1. Add the Discord bot to the server, if you haven't already.
2. Install `node` on your machine, if you haven't already.
3. Install mysql, start your mysql server, and create a database for the bot.
4. Create an `ormconfig.json` file like the following in the root of the project, including the configuration for the database you just created:
```
// ormconfig.json

{
  "type": "mysql",
  "host": "localhost",
  "port": 3306,
  "username": "<your mysql username>",
  "password": "<your mysql password>",
  "database": "<name of the database you just created>",
  "synchronize": true,
  "logging": false,
  "entities": ["build/bot/database/entities/*.js"],
  "migrations": ["build/bot/database/migrations/*.js"],
  "subscribers": ["build/bot/database/subscribers/*.js"],
  "cli": {
    "entitiesDir": "build/bot/database/entities",
    "migrationsDir": "build/bot/database/migrations",
    "subscribersDir": "build/bot/database/subscribers"
  }
}
```
5. Create `private.ts` under the `lib/bot/config/` directory, and populate it with these constants:
```
// private.ts

export const adminDiscordIds = ['<a discord ID you want monthly updates sent to>', ...];
export const databasePassword = '<password of the mysql database>';
export const discordBotId = '<the ID of your Discord bot's application>';
```
6. Run `npm i` to install your `node_modules`.
7. Run `npm run build` to compile the source code (yes I know I could bundle this into `npm start` but I'm lazy, leave me alone).
8. Run `npm start`.
9. That's it!
