import { headers, api_url } from './query'

export type Schemas = {
    [key: string]: Schema,
}
export interface Schema {
    tables: TablesMap;
    views: TablesMap;
    defaults?: string[];
}
export type TablesMap = Record<string, TableDefinition>;
type MarkdownEntry = { h?: string; t?: string };
interface ColumnDefinition {
  name: string;
  type: string;
  size?: number;
  unit?: string;
  default?: string|null;
  description?: string;
  unified_content_descriptor?: string;
  casu_keyword?: string;
  derived_from?: string;
  fits_ttype?: string;
}
export interface TableDefinition {
  schema: string;
  name: string;
  markdown?: MarkdownEntry[];
  // columns is a mapping of columnKey -> ColumnDefinition
  columns: Record<string, ColumnDefinition>;
  primary_keys?: string[];
  references?: ForeignKey[];
  statement?: string[];
  // allow additional unknown table-level keys
  [extra: string]: unknown;
}
interface ForeignKey {
    sourceCol: string[];
    target: string;
    targetCol: string[];
}

export const getDatabaseSchema = async() => {    
    const url = `${api_url}/schema`
    const response = await fetch(
        url,
        {
            headers: headers,
        }
    )
    if (response.status == 200) {
        const schema:Schemas = await response.json()
        return schema
    } else {
        return undefined
    }
}
