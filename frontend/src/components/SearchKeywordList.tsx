/* eslint-disable no-script-url */

import React from 'react';
import { observer } from 'mobx-react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';
import { StoreProps } from '../types/PropsTypes'

export const SearchKeywordList: React.FC<StoreProps> = observer(({ store }) => {
  let table, title
  if (store.searchResults.length > 0) {
    const resultCountLabel = store.searchResults.length === 100 ? "100+" : store.searchResults.length.toString()
    title = `Found ${resultCountLabel} keywords matching "${store.searchTerm}"`
    table = (
      <Table size="small">
      <TableHead>
        <TableRow>
          <TableCell>Name</TableCell>
          <TableCell>Collection</TableCell>
          <TableCell>Description</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {store.searchResults.map(keyword => (
          <TableRow key={keyword.id}>
            <TableCell>{keyword.collection.name}</TableCell>
            <TableCell>{keyword.name}</TableCell>
            <TableCell>{keyword.synopsis}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
    )
  } else {
    title = "No keywords found"
  }
  return (
    <React.Fragment>
      <Title>{title}</Title>
      {table}
    </React.Fragment>
  )
  });  
export default SearchKeywordList