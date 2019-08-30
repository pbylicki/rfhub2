import React from 'react';
import Typography from '@material-ui/core/Typography';

export const Title: React.SFC = (props) => (
  <Typography component="h2" variant="h6" color="primary" gutterBottom>
    {props.children}
  </Typography>
);

export default Title;
