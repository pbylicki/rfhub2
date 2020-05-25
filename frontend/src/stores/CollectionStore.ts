import axios, { AxiosResponse } from 'axios';
import { observable, action, computed } from 'mobx';
import { Collection, Keyword, VersionInfo } from '../types/ModelTypes';

export class CollectionStore {
  @observable collectionsMap: Map<number, Collection> = new Map()
  @observable collectionHasMore: boolean = false
  @observable searchTerm: string = ""
  @observable searchHasMore: boolean = false
  @observable searchResults: Map<number, Keyword> = new Map()
  @observable drawerSelectedCollection: number = 0
  @observable detailCollection: Collection | null = null
  @observable selectedKeywordId: number | null = null
  @observable versionInfo: VersionInfo | null = null
  @observable loading = {
    searchKeywords: false,
    getCollections: false,
    getCollection: false,
  }

  constructor() {
    this.getVersionInfo()
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
  getVersionInfo(): Promise<void> {
    return axios.get(`/api/v1/version/`)
      .then(resp => {
        this.versionInfo = resp.data;
      })
  }

  @action.bound
  getCollection(id: number): Promise<void> {
    this.loading.getCollection = true;
    this.selectedKeywordId = null;
    this.detailCollection = null;
    return axios.all([
      axios.get(`/api/v1/collections/stats/${id}/`),
      axios.get(`/api/v1/keywords/stats/?collection_id=${id}&limit=10000`)
    ])
    .then(axios.spread((collectionResp, keywordsResp) => {
      const collection = collectionResp.data;
      collection.keywords = keywordsResp.data;
      this.detailCollection = collection;
      this.loading.getCollection = false;
    }
    ))
  }

  @action.bound
  getCollectionWithKeywordSelected(collectionId: number, keywordId: number): void {
    this.getCollection(collectionId)
    this.selectedKeywordId = keywordId
  }

  @action.bound
  getCollections(skip: number = 0, limit: number = 100): Promise<void> {
    this.loading.getCollections = true;
    this.collectionHasMore = false
    return axios.get<any, AxiosResponse<Collection[]>>(`/api/v1/collections/stats/?skip=${skip}&limit=${limit}`)
      .then(resp => {
        const entries = new Map(resp.data.map((collection: Collection, index: number) => [skip + index, collection]));
        this.collectionsMap = new Map([...Array.from(this.collectionsMap), ...Array.from(entries)]);
        this.collectionHasMore = resp.data.length === limit;
        this.loading.getCollections = false;
      })
  }

  @action.bound
  clearSearchResults(): void {
    this.searchResults = new Map();
    this.searchHasMore = false;
  }

  @action.bound
  searchKeywords(pattern: string, skip: number = 0, limit: number = 100): Promise<void> {
    this.loading.searchKeywords = true;
    this.searchTerm = pattern;
    if (pattern.length > 0) {
      this.searchHasMore = false
      return axios.get<any, AxiosResponse<Keyword[]>>(`/api/v1/keywords/search/?pattern=${pattern}&skip=${skip}&limit=${limit}`)
        .then(resp => {
          const entries = new Map(resp.data.map((keyword: Keyword, index: number) => [skip + index, keyword]));
          const searchHasMore = resp.data.length === limit;
          this.updateSearchResults(entries, searchHasMore);
          this.loading.searchKeywords = false;
        })
    } else {
      this.clearSearchResults();
      return Promise.resolve()
    }
  }

  @action.bound
  updateSearchResults(searchResults: Map<number, Keyword>, hasMore: boolean): void {
    this.searchResults = new Map([...Array.from(this.searchResults), ...Array.from(searchResults)]);;
    this.searchHasMore = hasMore;
  }
}

export const collectionStore: CollectionStore = new CollectionStore()
