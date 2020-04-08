import React from 'react';
import ColorHash from 'color-hash';
import Chip from '@material-ui/core/Chip';
import { makeStyles } from '@material-ui/core/styles';

interface TagChipProps {
    tag: string,
    backgroundColor: string
}

const TagChip: React.FC<TagChipProps> = ({ tag, backgroundColor }) => {
    const styles = makeStyles({
        root: {
            backgroundColor: backgroundColor,
            color: 'white',
            fontWeight: 'bold',
            margin: 2
        }
    })()
    return (
        <Chip label={tag} className={styles.root} />
    )
}

class TagChipFactory {
    private colorHash: ColorHash;

    constructor() {
        this.colorHash = new ColorHash()
    }

    private toRGBString(RGBArray: number[], threshold: number): string {
        //if any color code is higher than provided threshold,
        //override it with the value of threshold minus difference between threshold and original code
        //it is done to filter out light colors that would make white label inside less readable
        const adjustedRGB = RGBArray.map(value => value > threshold ? threshold - (value % threshold) : value);
        return `rgb(${adjustedRGB.join()})`
    }

    get(tag: string, colorThreshold: number = 170): JSX.Element {
        const RBGArray = this.colorHash.rgb(tag)
        const RGBString = this.toRGBString(RBGArray, colorThreshold)
        return (
            <TagChip tag={tag} backgroundColor={RGBString} />
        )
    }
}

export default new TagChipFactory()
