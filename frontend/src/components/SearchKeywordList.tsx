/* eslint-disable no-script-url */

import React from 'react';
import { observer } from 'mobx-react';
import { Link } from 'react-router-dom';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import VisibilitySensor from 'react-visibility-sensor';
import Title from './Title';
import { Keyword } from '../types/ModelTypes';
import { StoreProps } from '../types/PropsTypes';
import { List } from '@material-ui/core';

interface SearchKeywordItemProps {
  keyword: Keyword;
}

const SearchKeywordItem: React.FC<SearchKeywordItemProps> = ({ keyword }) => {
  const keywordPrimaryText = `${keyword.name} (${keyword.collection.name})`
  return (
    <ListItem key={keyword.id}>
      <Link to={`/keywords/${keyword.collection.id}/${keyword.id}/`}>
        <ListItemText primary={keywordPrimaryText} secondary={keyword.synopsis} />
      </Link>
    </ListItem>
  );
}

export const SearchKeywordList: React.FC<StoreProps> = observer(({ store }) => {
  const loadMore = () => store.searchKeywords(store.searchTerm, store.searchResults.size)

  let table, title
  if (store.searchResults.size > 0) {
    const resultCountLabel = store.searchResults.size >= 100 ? "100+" : store.searchResults.size.toString()
    title = `Found ${resultCountLabel} keywords matching "${store.searchTerm}"`
    table = (
      <List>
        {Array.from(store.searchResults.values()).map((keyword, index) => {
          if (store.searchHasMore && index === store.searchResults.size - 3) {
            return (
              <VisibilitySensor key={keyword.id}>
                {({ isVisible }) => {
                  if (isVisible) {
                    loadMore()
                  }
                  return (<SearchKeywordItem keyword={keyword} />)
                }}
              </VisibilitySensor>)
          } else {
            return (<SearchKeywordItem key={keyword.id} keyword={keyword} />)
          }
        }
        )}
      </List>
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
