/* eslint-disable no-script-url */

import React from 'react';
import { observer } from 'mobx-react';
import { Link } from 'react-router-dom';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import VisibilitySensor from 'react-visibility-sensor';
import Title from './Title';
import { Collection } from '../types/ModelTypes';
import { StoreProps } from '../types/PropsTypes';

interface CollectionTableRowProps {
  collection: Collection
}

const CollectionTableRow: React.FC<CollectionTableRowProps> = ({ collection }) => (
  <TableRow key={collection.id}>
    <TableCell><Link to={`/keywords/${collection.id}`}>{collection.name}</Link></TableCell>
    <TableCell>{collection.type}</TableCell>
    <TableCell>{collection.version}</TableCell>
    <TableCell align="right">{collection.keywords.length}</TableCell>
    <TableCell align="right">{collection.times_used}</TableCell>
  </TableRow>
)

export const CollectionList: React.FC<StoreProps> = observer(({ store }) => {
  const loadMore = () => store.getCollections(store.collections.length)
  const resultCountLabel = store.collectionHasMore ? `${store.collections.length}+` : store.collections.length.toString()
  return (
  <React.Fragment>
    <Title>Collections ({resultCountLabel})</Title>
    <Table size="small">
      <TableHead>
        <TableRow>
          <TableCell>Name</TableCell>
          <TableCell>Type</TableCell>
          <TableCell>Version</TableCell>
          <TableCell align="right">Keywords</TableCell>
          <TableCell align="right">Times used</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {store.collections.map((collection, index) => {
          if (store.collectionHasMore && index === store.collections.length - 3) {
            return (
              <VisibilitySensor key={collection.id}>
                {({ isVisible }) => {
                  if (isVisible) {
                    loadMore()
                  }
                  return (<CollectionTableRow collection={collection} />)
                }}
              </VisibilitySensor>)
          } else {
            return (<CollectionTableRow key={collection.id} collection={collection} />)
          }
        })}
      </TableBody>
    </Table>
  </React.Fragment>
)});
export default CollectionList