// eslint-disable-next-line node/no-unpublished-import
import { GuardFunction, Client, Next, ArgsOf } from '@typeit/discord';
import { Message } from 'discord.js';
import {
  channelBlocklist,
  Role,
  staffChannelCategories,
} from '../common/constants';

/**
 * Helper function to create guards that are simple conditionals.
 */
function createConditionalGuard(
  canProceed: (
    message: ArgsOf<'message'>,
    client: Client,
    next: Next
  ) => boolean
): GuardFunction<'message'> {
  return (messages, client, next) => {
    if (canProceed(messages, client, next)) next();
  };
}

/**
 * Verifies that the triggered message is a DM.
 */
export const isDirectMessage: GuardFunction<'message'> = createConditionalGuard(
  ([message]) => message.channel.type === 'dm'
);

/**
 * Verifies that the triggered message is not in the channel blocklist.
 */
export const isValidChannel: GuardFunction<'message'> = createConditionalGuard(
  ([message]) => !(message.channel.toString() in channelBlocklist)
);

/**
 * Verifies that the message-triggering user is not Wanderbot.
 */
export const isUser: GuardFunction<'message'> = createConditionalGuard(
  ([message]) => message.author.bot
);

export const isStaffChannel: GuardFunction<'message'> = createConditionalGuard(
  ([message]) =>
    message.channel.type === 'text' &&
    staffChannelCategories.includes(message.channel.parent.name)
);

/**
 * Verifies the message-triggering user has the provided role.
 */
export const hasRole = (role: Role) =>
  createConditionalGuard(([message]) => containsRole(message, role));

/**
 * Verifies the message-triggering user any the provided role.
 */
export const hasAnyRole = (roles: Role[]) =>
  createConditionalGuard(([message]) =>
    roles.some(role => containsRole(message, role))
  );

const containsRole = (message: Message, role: Role): boolean => {
  const roles = [...(message.member?.roles.cache.values() ?? [])].map(
    cachedRole => cachedRole.name
  );
  return (
    roles.includes(role.toString()) || roles.includes(Role.wanderbotsFriend)
  );
};
