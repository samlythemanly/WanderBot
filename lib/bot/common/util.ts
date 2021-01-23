import * as asciiTable from 'ascii-table';
import { Character } from '../database/entities/character';

export function createTable(
  header: string,
  character: Character,
  fields: string[]
): unknown {
  const table = new asciiTable(`${header}`);

  table.setHeading(_createHeading(fields));
  table.addRow(_createRows(character, fields));

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
  while (characters.length > 0) {
    const page = characters.slice(0, 5);

    const table = new asciiTable(
      `${header} (Page ${pageNumber} of ${totalPages})`
    );

    table.setHeading(_createHeading(fields));

    for (const character of page) {
      table.addRow(_createRows(character, fields));
    }

    tables.push(table);
    pageNumber++;
  }

  return tables;
}

function _createHeading(fields: string[]): string[] {
  const columns = [];

  if (fields['id']) columns.push('ID');
  if (fields['name']) columns.push('Character');
  if (fields['owner']) columns.push('Owner');
  if (fields['monthlyPostCount']) columns.push('Monthly post count');
  if (fields['postCount']) columns.push('Total posts');
  if (fields['isNew']) columns.push('Is new?');
  if (fields['isOnProbation']) columns.push('Is on probation?');
  if (fields['isArchived']) columns.push('Is archived?');

  return columns;
}

function _createRows(character: Character, fields: string[]): unknown[] {
  const columns = [];

  if (fields['id']) columns.push(character.id);
  if (fields['name']) columns.push(character.name);
  if (fields['owner']) columns.push(character.owner.name);
  if (fields['monthlyPostCount']) columns.push(character.monthlyPostCount);
  if (fields['postCount']) columns.push(character.postCount);
  if (fields['isNew']) columns.push(character.isNew);
  if (fields['isOnProbation']) columns.push(character.isOnProbation);
  if (fields['isArchived']) columns.push(character.isArchived);

  return columns;
}
