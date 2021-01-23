import 'reflect-metadata';
import { Bot } from './bot';
import container from './bot/config/inversify.config';

const bot = container.get(Bot);
bot.start();
