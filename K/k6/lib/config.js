export const BASE_URL = __ENV.BASE_URL || 'https://frasers-stg-fh-ase6ecd8gmfza9h9.a01.azurefd.net';

export const PATHS = {
  offersHotelList: '/content/frasers-hospitality/en/offers.hotelsArrList.json',
  offersList: '/content/frasers-hospitality/en/offers.offerList.json',
  locationsPropertyListing: '/content/frasers-hospitality/en/locations.propertylisting.sidebar.json',
};

export const OFFERS_LIST_QUERY = {
  component: 'offerListingV2',
  componentPath: '/content/frasers-hospitality/en/offers/jcr:content/root/container/offer_listing',
  currency: 'USD',
  pageNumber: '1',
};

export const THRESHOLDS_MS = {
  offersHotelList: Number(__ENV.OFFERS_HOTEL_MAX_MS || 3000),
  lightApi: Number(__ENV.HEALTH_MAX_MS || 1000),
};

export const THINK_TIME_MIN_S = 0.5;
export const THINK_TIME_MAX_S = 1.5;
