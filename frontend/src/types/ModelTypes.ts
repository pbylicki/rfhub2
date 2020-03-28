export interface Keyword {
    id: number
    name: string
    doc: string
    args: string | null
    arg_string: string
    synopsis: string
    html_doc: string
    collection: NestedCollection
}

export interface NestedKeyword {
    id: number
    name: string
    doc: string
    args: string | null
    arg_string: string
    synopsis: string
    html_doc: string
    times_used: number | null
    avg_elapsed: number | null
}

export interface Collection {
    id: number
    name: string
    doc: string
    type: string
    version: string | null
    scope: string | null
    path: string | null
    synopsis: string
    html_doc: string
    keywords: NestedKeyword[]
    times_used: number | null
}

export interface NestedCollection {
    id: number
    name: string
}

export interface VersionInfo {
    title: string
    version: string
}