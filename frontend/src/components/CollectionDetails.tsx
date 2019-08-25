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

export const CollectionDetails: React.FC<StoreProps> = observer(({ store }) =>
(<React.Fragment>
  {store.collections.map(collection => (
      <React.Fragment>
        <Title>{store.collections[0].name}</Title>
        <div>{store.collections[0].doc}</div>
        <Title>Keywords ({store.collections[0].keywords.length})</Title>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Keyword</TableCell>
              <TableCell>Arguments</TableCell>
              <TableCell>Documentation</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {store.collections[0].keywords.map(keyword => (
              <TableRow key={keyword.id}>
                <TableCell>{keyword.name}</TableCell>
                <TableCell>{keyword.args}</TableCell>
                <TableCell>{keyword.doc}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </React.Fragment>
    ))}
    </React.Fragment>)
    );  
export default CollectionDetails