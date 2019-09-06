import React from 'react';
import { observer } from 'mobx-react';
import ExternalLink from '@material-ui/core/Link';
import Typography from '@material-ui/core/Typography';
import { StoreProps } from '../types/PropsTypes';

export const Copyright: React.FC<StoreProps> = observer(({ store }) => {
    const version = store.versionInfo ? `version ${store.versionInfo.version}` : ""
    return (
        <Typography variant="body2" color="textSecondary" align="center">
            <ExternalLink color="inherit" href="https://github.com/pbylicki/rfhub2">
                rfhub2
          </ExternalLink>
            {` ${version}`}
        </Typography>
    );
})

export default Copyright