import { useState, useEffect, useCallback } from 'react'
import { api, type FilterParams } from '@/services/api'
import type {
  OverviewData,
  TrendData,
  HourlyData,
  TopShowsData,
  TopContentData,
  UsersData,
  ClientsData,
  PlaybackMethodsData,
  DevicesData,
  RecentData,
  NowPlayingData,
} from '@/types'

// 序列化筛选参数用于依赖比较
function serializeParams(params: FilterParams): string {
  return JSON.stringify(params)
}

export function useOverview(params: FilterParams) {
  const [data, setData] = useState<OverviewData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const paramsKey = serializeParams(params)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getOverview(params)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useTrend(params: FilterParams) {
  const [data, setData] = useState<TrendData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const paramsKey = serializeParams(params)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getTrend(params)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useHourly(params: FilterParams) {
  const [data, setData] = useState<HourlyData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const paramsKey = serializeParams(params)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getHourly(params)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useTopShows(params: FilterParams, limit = 16) {
  const [data, setData] = useState<TopShowsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const paramsKey = serializeParams(params)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getTopShows(params, limit)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey, limit])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useTopContent(params: FilterParams, limit = 18) {
  const [data, setData] = useState<TopContentData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const paramsKey = serializeParams(params)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getTopContent(params, limit)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey, limit])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useUsers(params: FilterParams) {
  const [data, setData] = useState<UsersData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const paramsKey = serializeParams(params)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getUsers(params)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useClients(params: FilterParams) {
  const [data, setData] = useState<ClientsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const paramsKey = serializeParams(params)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getClients(params)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function usePlaybackMethods(params: FilterParams) {
  const [data, setData] = useState<PlaybackMethodsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const paramsKey = serializeParams(params)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getPlaybackMethods(params)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useDevices(params: FilterParams) {
  const [data, setData] = useState<DevicesData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const paramsKey = serializeParams(params)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getDevices(params)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useRecent(params: FilterParams, limit = 48, offset = 0) {
  const [data, setData] = useState<RecentData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const paramsKey = serializeParams(params)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getRecent(params, limit, offset)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey, limit, offset])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useNowPlaying(refreshInterval = 10000) {
  const [data, setData] = useState<NowPlayingData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetch = useCallback(async () => {
    try {
      const result = await api.getNowPlaying()
      setData(result)
      setError(null)
    } catch (e) {
      setError(e as Error)
      setData({ now_playing: [] })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetch()
    const timer = setInterval(fetch, refreshInterval)
    return () => clearInterval(timer)
  }, [fetch, refreshInterval])

  return { data, loading, error, refetch: fetch }
}
