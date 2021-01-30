import * as asciiTable from 'ascii-table';
import { Character } from '../database/entities/character';

/**
 * Creates a list of ascii tables to be sent as a message to a user or channel.
 * @param header String to be displayed in the table header along with the
 *               current page number.
 * @param characters The characters to be displayed in the table.
 * @param fields Which character fields to display as columns in the table.
 * @param shouldShowPageCount Whether to display the page count in the header.
 * @returns A list of ascii tables, paginated every 5 characters. (The type is
 *          unknown because the ascii-table library doesn't have any types).
 */
export function createTables(
  header: string,
  characters: Character[],
  fields: string[],
  shouldShowPageCount: boolean = true
): unknown[] {
  const sortedCharacters = characters.sort((a, b) =>
    a.name.localeCompare(b.name)
  );
  const tables = [];
  const totalPages =
    Math.floor(sortedCharacters.length / 5) +
    (sortedCharacters.length % 5 > 0 ? 1 : 0);
  for (let pageNumber = 1; pageNumber <= totalPages; pageNumber++) {
    const page = sortedCharacters.slice((pageNumber - 1) * 5, pageNumber * 5);

    const table = new asciiTable(
      `${header}${
        shouldShowPageCount ? ` (Page ${pageNumber} of ${totalPages})` : ''
      }`
    );

    table.setHeading(_createHeading(fields));

    for (const character of page) {
      table.addRow(..._createRow(character, fields));
    }

    tables.push(table);
  }

  return tables;
}

function _createHeading(fields: string[]): string[] {
  const columns = [];

  if (fields.includes('id')) columns.push('ID');
  if (fields.includes('name')) columns.push('Name');
  if (fields.includes('nickname')) columns.push('Nickname');
  if (fields.includes('owner')) columns.push('Owner');
  if (fields.includes('monthlyPostCount')) columns.push('Monthly posts');
  if (fields.includes('postCount')) columns.push('Total posts');
  if (fields.includes('isNew')) columns.push('New?');
  if (fields.includes('isOnProbation')) columns.push('On probation?');
  if (fields.includes('isArchived')) columns.push('Archived?');

  return columns;
}

function _createRow(character: Character, fields: string[]): unknown[] {
  const columns = [];

  if (fields.includes('id')) columns.push(character.id);
  if (fields.includes('name')) columns.push(character.name);
  if (fields.includes('nickname')) columns.push(character.nickname ?? 'None');
  if (fields.includes('owner')) columns.push(character.owner?.name ?? 'None');
  if (fields.includes('monthlyPostCount'))
    columns.push(character.monthlyPostCount);
  if (fields.includes('postCount')) columns.push(character.postCount);
  if (fields.includes('isNew')) columns.push(character.isNew);
  if (fields.includes('isOnProbation')) columns.push(character.isOnProbation);
  if (fields.includes('isArchived')) columns.push(character.isArchived);

  return columns;
}
