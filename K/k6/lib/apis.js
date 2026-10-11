import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, PATHS, OFFERS_LIST_QUERY, THINK_TIME_MIN_S, THINK_TIME_MAX_S } from './config.js';
import { defaultHeaders } from './headers.js';

function thinkTime() {
  sleep(THINK_TIME_MIN_S + Math.random() * (THINK_TIME_MAX_S - THINK_TIME_MIN_S));
}

function queryString(params) {
  return Object.entries(params)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
}

export function runOffersHotelList() {
  const res = http.get(`${BASE_URL}${PATHS.offersHotelList}`, {
    headers: defaultHeaders,
    tags: { name: 'Offers Hotel List' },
  });

  let body;
  try {
    body = res.json();
  } catch (e) {
    body = null;
  }

  check(res, {
    'Offers Hotel List: status 200': (r) => r.status === 200,
    'Offers Hotel List: body contains hotels': (r) => r.body && r.body.includes('"hotels"'),
    'Offers Hotel List: country exists': () => body && body[0] && body[0].country,
    'Offers Hotel List: hotelID exists': () => body && body[0] && body[0].hotels && body[0].hotels[0] && body[0].hotels[0].hotelID,
  });

  thinkTime();
}

export function runOffersList() {
  const url = `${BASE_URL}${PATHS.offersList}?${queryString(OFFERS_LIST_QUERY)}`;
  const res = http.get(url, {
    headers: defaultHeaders,
    tags: { name: 'Offers List' },
  });

  let body;
  try {
    body = res.json();
  } catch (e) {
    body = null;
  }

  const offers = body && body[0] && body[0]['regional-offer'];

  check(res, {
    'Offers List: status 200': (r) => r.status === 200,
    'Offers List: body contains regional-offer': (r) => r.body && r.body.includes('"regional-offer"'),
    'Offers List: offerName exists': () => offers && offers[0] && offers[0].offerName,
  });

  thinkTime();
}

export function runLocationsPropertyListing() {
  const res = http.get(`${BASE_URL}${PATHS.locationsPropertyListing}`, {
    headers: defaultHeaders,
    tags: { name: 'Locations Property Listing' },
  });

  let body;
  try {
    body = res.json();
  } catch (e) {
    body = null;
  }

  check(res, {
    'Locations Property Listing: status 200': (r) => r.status === 200,
    'Locations Property Listing: body contains countryId': (r) => r.body && r.body.includes('"countryId"'),
    'Locations Property Listing: country exists': () => body && body[0] && body[0].country,
    'Locations Property Listing: hotelID exists': () => body && body[0] && body[0].hotels && body[0].hotels[0] && body[0].hotels[0].hotelID,
  });

  thinkTime();
}

export function runAllApis() {
  runOffersHotelList();
  runOffersList();
  runLocationsPropertyListing();
}
