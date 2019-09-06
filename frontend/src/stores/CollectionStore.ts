import axios, { AxiosResponse } from 'axios';
import { observable, action, computed } from 'mobx';
import { Collection, Keyword } from '../types/ModelTypes';

export class CollectionStore {
  @observable collectionsMap: Map<number, Collection> = new Map()
  @observable collectionHasMore: boolean = false
  @observable searchTerm: string = ""
  @observable searchHasMore: boolean = false
  @observable searchResults: Map<number, Keyword> = new Map()
  @observable drawerSelectedCollection: number = 0
  @observable detailCollection: Collection | null = null
  @observable selectedKeywordId: number | null = null

  constructor() {
    this.getCollections()
  }

  @computed
  get collections(): Collection[] {
    return Array.from(this.collectionsMap.values())
  }

  @action.bound
  toggleDrawerSelectedCollection(colIndex: number) {
    if (this.drawerSelectedCollection === colIndex) {
      this.drawerSelectedCollection = 0;
    } else {
      this.drawerSelectedCollection = colIndex;
    }
  }

  @action.bound
  getCollection(id: number): Promise<void> {
    this.selectedKeywordId = null;
    this.detailCollection = null;
    return axios.get(`/api/v1/collections/${id}/`)
      .then(resp => {
        this.detailCollection = resp.data;
      })
  }

  @action.bound
  getCollectionWithKeywordSelected(collectionId: number, keywordId: number): void {
    this.getCollection(collectionId)
    this.selectedKeywordId = keywordId
  }

  @action.bound
  getCollections(skip: number = 0, limit: number = 100): Promise<void> {
    this.collectionHasMore = false
    return axios.get<any, AxiosResponse<Collection[]>>(`/api/v1/collections/?skip=${skip}&limit=${limit}`)
      .then(resp => {
        const entries = new Map(resp.data.map((collection: Collection, index: number) => [skip + index, collection]));
        this.collectionsMap = new Map([...Array.from(this.collectionsMap), ...Array.from(entries)]);
        this.collectionHasMore = resp.data.length === limit;
      })
  }

  @action.bound
  clearSearchResults(): void {
    this.searchResults = new Map();
    this.searchHasMore = false;
  }

  @action.bound
  searchKeywords(pattern: string, skip: number = 0, limit: number = 100): Promise<void> {
    if (pattern.length > 2) {
      this.searchHasMore = false
      return axios.get<any, AxiosResponse<Keyword[]>>(`/api/v1/keywords/search/?pattern=${pattern}&skip=${skip}&limit=${limit}`)
        .then(resp => {
          const entries = new Map(resp.data.map((keyword: Keyword, index: number) => [skip + index, keyword]));
          this.searchResults = new Map([...Array.from(this.searchResults), ...Array.from(entries)]);
          this.searchTerm = pattern;
          this.searchHasMore = resp.data.length === limit;
        })
    } else {
      this.clearSearchResults();
      this.searchTerm = pattern;
      return Promise.resolve()
    }
  }
}

export const collectionStore: CollectionStore = new CollectionStore()
