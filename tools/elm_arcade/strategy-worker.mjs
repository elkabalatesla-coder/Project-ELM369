import {optimalHolds} from './math/poker.mjs';

self.onmessage = ({data}) => {
  try { self.postMessage({result: optimalHolds(data.hand, data.variant)}); }
  catch (error) { self.postMessage({error: error.message}); }
};
