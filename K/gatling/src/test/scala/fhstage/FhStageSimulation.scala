package fhstage

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class FhStageSimulation extends Simulation {

  private val baseUrl = "https://frasers-stg-fh-ase6ecd8gmfza9h9.a01.azurefd.net"
  private val offersHotelMaxMs = sys.props.get("offersHotelMaxMs").map(_.toInt).getOrElse(3000)
  private val healthMaxMs = sys.props.get("healthMaxMs").map(_.toInt).getOrElse(1000)

  private val httpProtocol = http
    .baseUrl(baseUrl)
    .acceptHeader("application/json, text/javascript, */*; q=0.01")
    .acceptLanguageHeader("en-US,en;q=0.9")
    .header("sec-fetch-mode", "cors")
    .header("sec-fetch-site", "same-origin")
    .header("x-requested-with", "XMLHttpRequest")
    .contentTypeHeader("application/json")
    .shareConnections

  private val offersListQuery = Map(
    "component" -> "offerListingV2",
    "componentPath" -> "/content/frasers-hospitality/en/offers/jcr:content/root/container/offer_listing",
    "currency" -> "USD",
    "pageNumber" -> "1"
  )

  private val apiScenario = scenario("FH Stage API Load Test")
    .exec(
      http("Offers Hotel List")
        .get("/content/frasers-hospitality/en/offers.hotelsArrList.json")
        .check(status.is(200))
        .check(substring("\"hotels\"").exists)
        .check(jsonPath("$[0].country").exists)
        .check(jsonPath("$[0].hotels[0].hotelID").exists)
    )
    .pause(500.milliseconds, 1500.milliseconds)
    .exec(
      http("Offers List")
        .get("/content/frasers-hospitality/en/offers.offerList.json")
        .queryParamMap(offersListQuery)
        .check(status.is(200))
        .check(substring("\"regional-offer\"").exists)
        .check(jsonPath("$[0]['regional-offer'][0].offerName").exists)
    )
    .pause(500.milliseconds, 1500.milliseconds)
    .exec(
      http("Locations Property Listing")
        .get("/content/frasers-hospitality/en/locations.propertylisting.sidebar.json")
        .check(status.is(200))
        .check(substring("\"countryId\"").exists)
        .check(jsonPath("$[0].country").exists)
        .check(jsonPath("$[0].hotels[0].hotelID").exists)
    )
    .pause(500.milliseconds, 1500.milliseconds)

  private val loadProfile = Option(System.getProperty("loadProfile")).getOrElse("1")

  private val injectionProfile = loadProfile match {
    case "10" =>
      apiScenario.inject(
        rampConcurrentUsers(10).during(10.seconds),
        constantConcurrentUsers(10).during(80.seconds)
      )
    case "50" =>
      apiScenario.inject(
        rampConcurrentUsers(50).during(25.seconds),
        constantConcurrentUsers(50).during(155.seconds)
      )
    case "100" =>
      apiScenario.inject(
        rampConcurrentUsers(100).during(30.seconds),
        constantConcurrentUsers(100).during(210.seconds)
      )
    case _ =>
      apiScenario.inject(
        rampConcurrentUsers(1).during(1.second),
        constantConcurrentUsers(1).during(60.seconds)
      )
  }

  setUp(injectionProfile)
    .protocols(httpProtocol)
    .assertions(
      global.successfulRequests.percent.gt(99),
      details("Offers Hotel List").responseTime.percentile3.lte(offersHotelMaxMs),
      details("Offers List").responseTime.percentile3.lte(healthMaxMs),
      details("Locations Property Listing").responseTime.percentile3.lte(healthMaxMs)
    )
}
