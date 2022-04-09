#!/usr/bin/env python

from dataclasses import astuple
from datetime import datetime
from utc_bot import UTCBot, start_bot
import proto.utc_bot as pb
import betterproto
import py_vollib.black_scholes
import py_vollib.black.implied_volatility
import py_vollib.black.greeks.analytical
# import py_vollib.black.greeks.analytical.gamma
# import py_vollib.black.greeks.analytical.vega
# import py_vollib.black.greeks.analytical.theta



import asyncio


option_strikes = [90, 95, 100, 105, 110]


class Case2ExampleBot(UTCBot):
    """
    An example bot for Case 2 of the 2021 UChicago Trading Competition. We recommend that you start
    by reading through this bot and understanding how it works. Then, make a copy of this file and
    start trying to write your own bot!
    """

    async def handle_round_started(self):
        """
        This function is called when the round is started. You should do your setup here, and
        start any tasks that should be running for the rest of the round.
        """

        # This variable will be a map from asset names to positions. We start out by initializing it
        # to zero for every asset.
        self.positions = {}

        self.positions["UC"] = 0
        for strike in option_strikes:
            for flag in ["C", "P"]:
                self.positions[f"UC{strike}{flag}"] = 0

        # Stores the current day (starting from 0 and ending at 5). This is a floating point number,
        # meaning that it includes information about partial days
        self.current_day = 0

        # Stores the current value of the underlying asset
        self.underlying_price = 100

    def compute_vol_estimate(self) -> float:
        """
        This function is used to provide an estimate of underlying's volatility. Because this is
        an example bot, we just use a placeholder value here. We recommend that you look into
        different ways of finding what the true volatility of the underlying is.
        """
        #"Computing vol less frequently, so the function has more time to run"
        #"Use the training data in the case2 file with the exchange to get a vol function"
        if self.current_day < 2.2:
          return 0.59
        elif self.current_day < 290:
          return 1.08
        else:
          return 1.46

    def compute_options_price(
        self,
        flag: str,
        underlying_px: float,
        strike_px: float,
        time_to_expiry: float,
        volatility: float,
    ) -> float:
        """
        This function should compute the price of an option given the provided parameters. Some
        important questions you may want to think about are:
            - What are the units associated with each of these quantities?
            - What formula should you use to compute the price of the option?
            - Are there tricks you can use to do this more quickly?
        You may want to look into the py_vollib library, which is installed by default in your
        virtual environment.
        """

        price = py_vollib.black_scholes.black_scholes(flag.lower(), underlying_px, strike_px, time_to_expiry, 0, volatility)
        #compute implied volatility every 30 days
        # print(self.current_day)

        # if int(self.current_day * 1000) % 30 == 0:
        #   iv = py_vollib.black.implied_volatility.implied_volatility(price, underlying_px, strike_px, time_to_expiry, 0, flag.lower())
        return price

    async def update_options_quotes(self):
        """
        This function will update the quotes that the bot has currently put into the market.

        In this example bot, the bot won't bother pulling old quotes, and will instead just set new
        quotes at the new theoretical price every time a price update happens. We don't recommend
        that you do this in the actual competition
        """
        #day 0 buy calls, timestep 220 sell call options and buy put options, timestep 290 buy calls at 90, 95, 100 sell puts
        
        # What should this value actually be?
        time_to_expiry = (26 - self.current_day)/252
        vol = self.compute_vol_estimate()

        requests = []

        print("current day:" + str(self.current_day))
        DELTA_LIMIT = 2000
        GAMMA_LIMIT = 5000
        VEGA_LIMIT = 1000000
        THETA_LIMIT = 500000
        print(self.current_day)

        total_delta = 0
        total_gamma = 0
        total_vega = 0
        total_theta = 0

        for strike in option_strikes:
            for flag in ["C", "P"]:
              #calculating greeks, but need to specify in flag if it is calculating for a call or a put option
              total_delta += self.positions["UC" + str(strike) + flag] * abs(py_vollib.black.greeks.analytical.delta(flag.lower(), self.underlying_price, strike, time_to_expiry, 0, vol))
              total_gamma += self.positions["UC" + str(strike) + flag] * abs(py_vollib.black.greeks.analytical.gamma(flag.lower(), self.underlying_price, strike, time_to_expiry, 0, vol))
              total_vega += self.positions["UC" + str(strike) + flag] * abs(py_vollib.black.greeks.analytical.vega(flag.lower(), self.underlying_price, strike, time_to_expiry, 0, vol))
              total_theta += self.positions["UC" + str(strike) + flag] * abs(py_vollib.black.greeks.analytical.theta(flag.lower(), self.underlying_price, strike, time_to_expiry, 0, vol))
        print(total_delta)
        if ((total_delta > (DELTA_LIMIT -1200)) or (total_gamma > (GAMMA_LIMIT -500))) or ((total_vega > (VEGA_LIMIT -100000)) or (total_theta > (THETA_LIMIT -50000))):
          print("self-liquidating to lower risk limits!")
          for strike in option_strikes:
            for flag in ["C", "P"]:
                asset_name = f"UC{strike}{flag}"
                theo = self.compute_options_price(
                    flag, self.underlying_price, strike, time_to_expiry, vol
                )

                requests.append(
                    self.place_order(
                        asset_name,
                        pb.OrderSpecType.LIMIT,
                        pb.OrderSpecSide.ASK,
                        5,
                        round(theo, 1) + 0.1,
                    )
                )

        else:
          if self.current_day == 0:
            for strike in option_strikes:
              for flag in ["C", "P"]:
                  asset_name = f"UC{strike}{flag}"
                  theo = self.compute_options_price(
                      flag, self.underlying_price, strike, time_to_expiry, vol
                  )

                  requests.append(
                      self.place_order(
                          asset_name,
                          pb.OrderSpecType.LIMIT,
                          pb.OrderSpecSide.BID,
                          1,  # How should this quantity be chosen?
                          round(theo, 1) - 0.30,  # How should this price be chosen?
                      )
                  )

                  requests.append(
                      self.place_order(
                          asset_name,
                          pb.OrderSpecType.LIMIT,
                          pb.OrderSpecSide.ASK,
                          1,
                          round(theo, 1) + 0.30,
                      )
                  )
          #day 0 buy calls, timestep 220 sell call options and buy put options, timestep 290 buy calls at 90, 95, 100 sell puts
          elif self.current_day < 2.2:
            for strike in option_strikes:
              for flag in ["P"]:
                  asset_name = f"UC{strike}{flag}"
                  theo = self.compute_options_price(
                      flag, self.underlying_price, strike, time_to_expiry, vol
                  )

                  requests.append(
                      self.place_order(
                          asset_name,
                          pb.OrderSpecType.LIMIT,
                          pb.OrderSpecSide.BID,
                          1,  # How should this quantity be chosen?
                          round(theo, 1) - 0.30,  # How should this price be chosen?
                      )
                  )
              for flag in ["C"]:
                  requests.append(
                      self.place_order(
                          asset_name,
                          pb.OrderSpecType.LIMIT,
                          pb.OrderSpecSide.ASK,
                          1,
                          round(theo, 1) + 0.30,
                      )
                  )
          elif self.current_day > 2.9:
            for strike in option_strikes:
              for flag in ["C"]:
                  asset_name = f"UC{strike}{flag}"
                  theo = self.compute_options_price(
                      flag, self.underlying_price, strike, time_to_expiry, vol
                  )

                  requests.append(
                      self.place_order(
                          asset_name,
                          pb.OrderSpecType.LIMIT,
                          pb.OrderSpecSide.BID,
                          1,  # How should this quantity be chosen?
                          round(theo, 1) - 0.30,  # How should this price be chosen?
                      )
                  )
              for flag in ["P"]:
                  requests.append(
                      self.place_order(
                          asset_name,
                          pb.OrderSpecType.LIMIT,
                          pb.OrderSpecSide.ASK,
                          1,
                          round(theo, 1) + 0.30,
                      )
                  )


        # optimization trick -- use asyncio.gather to send a group of requests at the same time
        # instead of sending them one-by-one
        responses = await asyncio.gather(*requests)
        for resp in responses:
            assert resp.ok

    async def handle_exchange_update(self, update: pb.FeedMessage):
        kind, _ = betterproto.which_one_of(update, "msg")

        if kind == "pnl_msg":
            # When you hear from the exchange about your PnL, print it out
            print("My PnL:", update.pnl_msg.m2m_pnl)

        elif kind == "fill_msg":
            # When you hear about a fill you had, update your positions
            fill_msg = update.fill_msg

            if fill_msg.order_side == pb.FillMessageSide.BUY:
                self.positions[fill_msg.asset] += update.fill_msg.filled_qty
            else:
                self.positions[fill_msg.asset] -= update.fill_msg.filled_qty
            print("now have " + str(self.positions[fill_msg.asset]) + " of "+ fill_msg.asset)

        elif kind == "market_snapshot_msg":
            # When we receive a snapshot of what's going on in the market, update our information
            # about the underlying price.
            book = update.market_snapshot_msg.books["UC"]
            # print(update.market_snapshot_msg)
            # Compute the mid price of the market and store it
            self.underlying_price = (
                float(book.bids[0].px) + float(book.asks[0].px)
            ) / 2

            await self.update_options_quotes()

        elif (
            kind == "generic_msg"
            and update.generic_msg.event_type == pb.GenericMessageType.MESSAGE
        ):
            # The platform will regularly send out what day it currently is (starting from day 0 at
            # the start of the case) 
            self.current_day = float(update.generic_msg.message)
            # print(self.current_day)
            # print(update.generic_msg.message)


if __name__ == "__main__":
    start_bot(Case2ExampleBot)