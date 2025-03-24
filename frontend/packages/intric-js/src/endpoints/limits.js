/** @typedef {import('../client/client').IntricError} IntricError */
/** @typedef {import('../types/resources').Limits} Limits */

/**
 * @param {import('../client/client').Client} client Provide a client with which to call the endpoints
 */
export function initLimits(client) {
  return {
    /**
     * Get info from the limits endpoint
     * @returns {Promise<Limits>} Get all the limits
     * @throws {IntricError}
     * */
    list: async () => {
      const res = await client.fetch("/api/v1/limits/", {
        method: "get"
      });
      return res;
    }
  };
}
