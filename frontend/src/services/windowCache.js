/**
 * Sliding-Window In-Memory Cache with Predictive Neighbor Preloading.
 * 
 * Features:
 * - Bounded LRU + Distance Eviction: maintains up to MAX_ENTRIES windows in memory.
 * - Out-of-Context Pruning: when capacity is reached, entries furthest from the active sampleIdx are evicted first.
 * - Predictive Preloading: asynchronously preloads 1 day before/after (-24h, +24h),
 *   2 days before/after (-48h, +48h), and adjacent steps (-1h, +1h).
 * - Deduplicated In-Flight Requests: prevents redundant concurrent HTTP queries.
 */

import { api } from './api';

const MAX_CACHE_ENTRIES = 50;

// Preload offsets requested by user:
// - Adjacent steps: -1h, +1h
// - 1 day before & after: -24h, +24h
// - 2 days before & after: -48h, +48h
const PRELOAD_OFFSETS = [-1, 1, -24, 24, -48, 48];

class WindowCache {
  constructor() {
    this.cache = new Map(); // key -> sampleData
    this.inFlight = new Map(); // key -> Promise<sampleData>
    this.preloadTimer = null;
  }

  _makeKey(station, sampleIdx) {
    return `${station || 'default'}:${sampleIdx}`;
  }

  has(station, sampleIdx) {
    return this.cache.has(this._makeKey(station, sampleIdx));
  }

  get(station, sampleIdx) {
    const key = this._makeKey(station, sampleIdx);
    if (!this.cache.has(key)) return undefined;
    // Refresh LRU order on access
    const val = this.cache.get(key);
    this.cache.delete(key);
    this.cache.set(key, val);
    return val;
  }

  set(station, sampleIdx, data, currentIdx = sampleIdx) {
    const key = this._makeKey(station, sampleIdx);
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
    this.cache.set(key, { ...data, _station: station, _sampleIdx: sampleIdx });
    this._evictOutOfContext(station, currentIdx);
  }

  _evictOutOfContext(station, currentIdx) {
    if (this.cache.size <= MAX_CACHE_ENTRIES) return;

    // Rank entries by temporal distance from active currentIdx
    const entries = Array.from(this.cache.entries()).map(([k, v]) => ({
      key: k,
      distance: Math.abs((v._sampleIdx ?? currentIdx) - currentIdx)
    }));

    // Sort descending: furthest entries first (out of context)
    entries.sort((a, b) => b.distance - a.distance);

    // Evict furthest until back within bounds
    while (this.cache.size > MAX_CACHE_ENTRIES && entries.length > 0) {
      const toRemove = entries.shift();
      if (toRemove) {
        this.cache.delete(toRemove.key);
      }
    }
  }

  /**
   * Fetch sample with cache-first strategy.
   * If already cached, returns immediately.
   * If already in-flight, returns shared promise.
   */
  async fetchSample(sampleIdx, station, currentIdx = sampleIdx) {
    const cached = this.get(station, sampleIdx);
    if (cached) return cached;

    const key = this._makeKey(station, sampleIdx);
    if (this.inFlight.has(key)) {
      return this.inFlight.get(key);
    }

    const promise = api.getSample(sampleIdx, station)
      .then(data => {
        this.set(station, sampleIdx, data, currentIdx);
        this.inFlight.delete(key);
        return data;
      })
      .catch(err => {
        this.inFlight.delete(key);
        throw err;
      });

    this.inFlight.set(key, promise);
    return promise;
  }

  /**
   * Schedule predictive preloading for 1 day before/after (-24h, +24h),
   * 2 days before/after (-48h, +48h), and adjacent steps (-1h, +1h).
   */
  preloadNeighbors(currentIdx, station, maxSamples = 26281) {
    if (this.preloadTimer) {
      clearTimeout(this.preloadTimer);
    }

    // Debounce preloading slightly (60ms) so rapid scrubber drags don't trigger intermediate bursts
    this.preloadTimer = setTimeout(() => {
      for (const offset of PRELOAD_OFFSETS) {
        const targetIdx = currentIdx + offset;
        if (targetIdx >= 0 && targetIdx < maxSamples) {
          if (!this.has(station, targetIdx)) {
            // Fetch in background, ignore failures quietly
            this.fetchSample(targetIdx, station, currentIdx).catch(() => {});
          }
        }
      }
    }, 60);
  }

  clear() {
    this.cache.clear();
    this.inFlight.clear();
  }
}

export const windowCache = new WindowCache();
export default windowCache;
