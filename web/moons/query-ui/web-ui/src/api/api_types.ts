export type QueryListResponse = {
  count: string,
  next: string | null,
  previous: string,
  results: [
    {
      id: Number,
      query: string,
      created: string,
      started: string,
      completed: string,
      current_status: string,
    }
  ],
}

