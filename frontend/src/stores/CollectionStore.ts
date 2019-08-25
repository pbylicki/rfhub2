import axios from 'axios';
import { observable, action } from 'mobx';

interface Keyword {
  id: number
  name: string
  doc: string
  args: string | null
  arg_string: string
  synopsis: string
  html_doc: string
  collection: NestedCollection
}

interface NestedKeyword {
    id: number
    name: string
    doc: string
    args: string | null
    arg_string: string
    synopsis: string
    html_doc: string
}

interface Collection {
  id: number
  name: string
  doc: string
  type: string
  version: string | null
  synopsis: string
  html_doc: string
  keywords: NestedKeyword[]
}

interface NestedCollection {
  id: number
  name: string 
}

export class CollectionStore {
  @observable collections: Collection[] = []
  @observable searchTerm: String = ""
  @observable searchResults: Keyword[] = []
  @observable drawerSelectedCollection: number = 0
  @observable detailCollection: Collection | null = null

  constructor() {
      this.getCollections()
  }

  @action.bound
  toggleDrawerSelectedCollection(colIndex: number) {
    if (this.drawerSelectedCollection === colIndex) {
      this.drawerSelectedCollection = 0;
    } else {
      this.drawerSelectedCollection = colIndex;
    }
    console.log(this.drawerSelectedCollection)
  }

  @action.bound
  getCollections(skip: number = 0, limit: number = 100): void {
    axios.get(`http://localhost:8000/api/v1/collections/?skip=${skip}&limit=${limit}`)
    .then(resp => {
        this.collections = resp.data;
        this.detailCollection = this.collections[0];
      })
  }

  @action.bound
  searchKeywords(pattern: String, skip: number = 0, limit: number = 100): void {
    if (pattern.length > 2) {
      axios.get(`http://localhost:8000/api/v1/keywords/search/?pattern=${pattern}&skip=${skip}&limit=${limit}`)
      .then(resp => {
          this.searchResults = resp.data;
        })
    } else {
      this.searchResults = [];
    }
    this.searchTerm = pattern;
  }
}

export const collectionStore: CollectionStore = new CollectionStore()