/* eslint-disable no-script-url */

import React from 'react';
import { observer } from 'mobx-react';
import { Link } from 'react-router-dom';
import { TableRow, TableCell, Table, TableHead, TableBody } from '@material-ui/core';
import VisibilitySensor from 'react-visibility-sensor';
import Title from './Title';
import { Keyword } from '../types/ModelTypes';
import { StoreProps } from '../types/PropsTypes';

interface SearchKeywordTableRowProps {
  keyword: Keyword;
}

const SearchKeywordTableRow: React.FC<SearchKeywordTableRowProps> = ({ keyword }) => (
  <TableRow key={keyword.id}>
    <TableCell><Link to={`/keywords/${keyword.collection.id}/${keyword.id}/`}>{keyword.name}</Link></TableCell>
    <TableCell>{keyword.collection.name}</TableCell>
    <TableCell>{keyword.synopsis}</TableCell>
  </TableRow>
)

export const SearchKeywordList: React.FC<StoreProps> = observer(({ store }) => {
  const loadMore = () => store.searchKeywords(store.searchTerm, store.searchResults.size)

  let table, title
  if (store.searchResults.size > 0) {
    const resultCountLabel = store.searchHasMore ? `${store.searchResults.size}+` : store.searchResults.size.toString()
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
          {Array.from(store.searchResults.values()).map((keyword, index) => {
            if (store.searchHasMore && index === store.searchResults.size - 3) {
              return (
                <VisibilitySensor key={keyword.id}>
                  {({ isVisible }) => {
                    if (isVisible) {
                      loadMore()
                    }
                    return (<SearchKeywordTableRow keyword={keyword} />)
                  }}
                </VisibilitySensor>)
            } else {
              return (<SearchKeywordTableRow key={keyword.id} keyword={keyword} />)
            }
          }
          )}
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
