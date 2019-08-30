/* eslint-disable no-script-url */

import React from 'react';
import { observer } from 'mobx-react';
import { Link } from 'react-router-dom';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';
import { StoreProps } from '../types/PropsTypes'

export const CollectionList: React.FC<StoreProps> = observer(({ store }) => (
  <React.Fragment>
    <Title>Collections ({store.collections.length})</Title>
    <Table size="small">
      <TableHead>
        <TableRow>
          <TableCell>Name</TableCell>
          <TableCell>Type</TableCell>
          <TableCell>Version</TableCell>
          <TableCell align="right">Keywords</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {store.collections.map(collection => (

          <TableRow key={collection.id}>
            <TableCell><Link to={`/keywords/${collection.id}`}>{collection.name}</Link></TableCell>
            <TableCell>{collection.type}</TableCell>
            <TableCell>{collection.version}</TableCell>
            <TableCell align="right">{collection.keywords.length}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </React.Fragment>
));
export default CollectionList