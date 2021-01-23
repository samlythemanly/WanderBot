import * as asciiTable from 'ascii-table';
import { Character } from '../database/entities/character';

export function createTable(
  header: string,
  character: Character,
  fields: string[]
): unknown {
  const table = new asciiTable(`${header}`);

  table.setHeading(_createHeading(fields));
  table.addRow(..._createRow(character, fields));

  return table;
}

export function createTables(
  header: string,
  characters: Character[],
  fields: string[]
): unknown[] {
  const tables = [];
  let pageNumber = 1;
  const totalPages =
    Math.floor(characters.length / 5) + (characters.length % 5 > 0 ? 1 : 0);
  while (pageNumber <= totalPages) {
    const page = characters.slice(0, 5);

    const table = new asciiTable(
      `${header} (Page ${pageNumber} of ${totalPages})`
    );

    table.setHeading(_createHeading(fields));

    for (const character of page) {
      table.addRow(..._createRow(character, fields));
    }

    tables.push(table);
    pageNumber++;
  }

  return tables;
}

function _createHeading(fields: string[]): string[] {
  const columns = [];

  if (fields.includes('id')) columns.push('ID');
  if (fields.includes('name')) columns.push('Character');
  if (fields.includes('owner')) columns.push('Owner');
  if (fields.includes('monthlyPostCount')) columns.push('Monthly post count');
  if (fields.includes('postCount')) columns.push('Total posts');
  if (fields.includes('isNew')) columns.push('Is new?');
  if (fields.includes('isOnProbation')) columns.push('Is on probation?');
  if (fields.includes('isArchived')) columns.push('Is archived?');

  return columns;
}

function _createRow(character: Character, fields: string[]): unknown[] {
  const columns = [];

  if (fields.includes('id')) columns.push(character.id);
  if (fields.includes('name')) columns.push(character.name);
  if (fields.includes('owner')) columns.push(character.owner?.name ?? 'None');
  if (fields.includes('monthlyPostCount'))
    columns.push(character.monthlyPostCount);
  if (fields.includes('postCount')) columns.push(character.postCount);
  if (fields.includes('isNew')) columns.push(character.isNew);
  if (fields.includes('isOnProbation')) columns.push(character.isOnProbation);
  if (fields.includes('isArchived')) columns.push(character.isArchived);

  return columns;
}
