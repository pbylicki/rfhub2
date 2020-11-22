import React from "react";
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Modal from '@material-ui/core/Modal';

function rand() {
    return Math.round(Math.random() * 20) - 10;
}

function getModalStyle() {
    const top = 50 + rand();
    const left = 50 + rand();
    return {
        top: `${top}%`,
        left: `${left}%`,
        transform: `translate(-${top}%, -${left}%)`,
    };
}

const useStyles = makeStyles(theme => ({
    modal: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    },
    paper: {
        position: 'absolute',
        width: 450,
        backgroundColor: theme.palette.background.paper,
        boxShadow: theme.shadows[5],
        padding: theme.spacing(2, 4, 3),
    },
}));

export default function SimpleModal() {
    const classes = useStyles();
    const [modalStyle] = React.useState(getModalStyle);
    const [open, setOpen] = React.useState(false);

    const handleOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    return (
        <div>
            <Button variant="contained" color="primary" onClick={handleOpen}>
                How to search
            </Button>

            <Modal
                aria-labelledby="simple-modal-title"
                aria-describedby="simple-modal-description"
                open={open}
                onClose={handleClose}
            >
                <div style={modalStyle} className={classes.paper}>
                    <h2>How to search</h2>
                    <p><strong>in:</strong> operator will narrow search only to library or resource, with matching name.
                        <br />Using <strong>Should in: BuiltIn</strong> will search for all keywords with Should in their names, coming from BuiltIn library.
                    </p>
                    <p><strong>tags:</strong> operator will narrow search to keywords tags.
                        <br />Using <strong>Tags: Manual</strong> will search for all keywords with Manual tag.
                    </p>
                    <h3>Combining operators</h3>
                    <p><strong>name: in:</strong> will search only in keywords name in assets with matching names.
                       <br />Using<strong> name: Should in: BuiltIn</strong> will search for all keywords
                       with Should in their names in BuiltIn library.
                    </p>
                    <p><strong>tags: in:</strong> will narrow search to tags in assets with matching names.
                       <br />Using <strong>tags: Manual in: keywords</strong> will search for keywords with Manual tag in
                       keyword resource.
                    </p>
                </div>
            </Modal>
        </div>
    );
}