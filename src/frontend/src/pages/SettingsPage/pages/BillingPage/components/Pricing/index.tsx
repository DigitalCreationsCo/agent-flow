import {Button} from '@/components/ui/button';
import { getErrorRedirect } from '@/utils/redirectUtils';
import { Users } from '@/types/api';
import { cn } from '@/utils/utils';
import { useState } from 'react';
import { Price, ProductWithPrices, SubscriptionWithProduct } from '@/types/billing';
import { useCustomNavigate } from '@/customization/hooks/use-custom-navigate';
import { useLocation } from 'react-router-dom';
import { useGetProducts } from '@/controllers/API/queries/stripe/use-get-products';
import { useGetSubscription } from '@/controllers/API/queries/stripe/use-get-subscription';
import { useGetPrices } from '@/controllers/API/queries/stripe/use-get-prices';
import Loading from '@/components/ui/loading';
import { api } from '@/controllers/API/api';
import { getURL } from '@/controllers/API/helpers/constants';

interface Props {
  user: Users | null | undefined;
  // products: ProductWithPrices[];
  // subscription: SubscriptionWithProduct | null;
}

type BillingInterval = 'lifetime' | 'year' | 'month';
export default function Pricing({ user }: Props) {
  const { data: subscription, isLoading: isSubscriptionLoading, isFetching: isSubscriptionFetching } = useGetSubscription(user?.subscription_id ?? '');
  const { data: products, isLoading: isProductsLoading, isFetching: isProductsFetching } = useGetProducts();
  const { data: prices, isLoading: isPricesLoading, isFetching: isPricesFetching } = useGetPrices();

  console.log(`products `, products)
  console.log(`prices `, prices)
  console.log(`subscription `, subscription)
  const intervals = Array.from(
    new Set(
      products?.flatMap((product) =>
        product?.prices?.map((price) => price?.interval)
      )
    )
  );
  const [billingInterval, setBillingInterval] =
  useState<BillingInterval>('month');
  const [priceIdLoading, setPriceIdLoading] = useState<string>();

  const navigate = useCustomNavigate();
  const location = useLocation();
  const currentPath = location.pathname;

  const handleStripeCheckout = async (price: Price) => {
    try {
      setPriceIdLoading(price.id);

      if (!user) {
        setPriceIdLoading(undefined);
        navigate('/signin/signup');
        return;
      }

      // Call the backend checkout endpoint
      const response = await api.post(`${getURL("CHECKOUT")}`, {
        price_id: price.id,
        redirect_path: currentPath
      });

      const { errorRedirect, sessionUrl, sessionId } = response.data;

      if (errorRedirect) {
        setPriceIdLoading(undefined);
        navigate(errorRedirect);
        return;
      }

      if (!sessionUrl) {
        setPriceIdLoading(undefined);
        navigate(
          getErrorRedirect(
            currentPath,
            'An unknown error occurred.',
            'Please try again later or contact a system administrator.'
          )
        );
        return;
      }

      // Redirect directly to Stripe's checkout URL
      window.location.href = sessionUrl;

    } catch (error) {
      console.error('Stripe checkout error:', error);
      navigate(
        getErrorRedirect(
          currentPath,
          'Payment initialization failed',
          'Unable to start checkout process. Please try again.'
        )
      );
    } finally {
      setPriceIdLoading(undefined);
    }
  };

  const allLoaded = !isProductsLoading && !isSubscriptionLoading && !isPricesLoading;

  if (!allLoaded) {
    return (
      <div className="flex h-full w-full items-center align-middle">
      <Loading></Loading>
      </div>
    )
  }

  if (!products?.length) {
    return (
      <section className="">
        <div className="max-w-6xl mx-auto">
          <div className="sm:flex sm:flex-col sm:align-center"></div>
          <p>
            No pricing plans found. Create them in your{' '}
            <a
              className="underline"
              href="https://dashboard.stripe.com/products"
              rel="noopener noreferrer"
              target="_blank"
            >
              Stripe Dashboard
            </a>
            .
          </p>
        </div>
      </section>
    );
  } else {
    return (
      <section className="max-w-6xl mx-auto h-full w-full grow">
        <div className="max-w-6xl h-full grow items-center justify-center m-auto rounded-md border">
          <div className="sm:flex sm:flex-col sm:align-center grow m-auto h-full justify-center items-center">
            {/* <h1>
              Pricing Plans
            </h1> */}
            <p className="max-w-2xl m-auto my-5">
              Start building for free ❤️
            </p>
            {/* <div className="relative self-center mt-6 bg-zinc-900 rounded-lg p-0.5 flex sm:mt-8 border border-zinc-800">
              {intervals.includes('month') && (
                <button
                  onClick={() => setBillingInterval('month')}
                  type="button"
                  className={`${
                    billingInterval === 'month'
                      ? 'relative w-1/2 bg-zinc-700 border-zinc-800 shadow-sm text-white'
                      : 'ml-0.5 relative w-1/2 border border-transparent text-zinc-400'
                  } rounded-md m-1 py-2 text-sm font-medium whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-opacity-50 focus:z-10 sm:w-auto sm:px-8`}
                >
                  Monthly billing
                </button>
              )}
              {intervals.includes('year') && (
                <button
                  onClick={() => setBillingInterval('year')}
                  type="button"
                  className={`${
                    billingInterval === 'year'
                      ? 'relative w-1/2 bg-zinc-700 border-zinc-800 shadow-sm text-white'
                      : 'ml-0.5 relative w-1/2 border border-transparent text-zinc-400'
                  } rounded-md m-1 py-2 text-sm font-medium whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-opacity-50 focus:z-10 sm:w-auto sm:px-8`}
                >
                  Yearly billing
                </button>
              )}
            </div> */}
          </div>
          {/* <div className="border mt-12 space-y-0 sm:mt-16 flex flex-wrap justify-center gap-6 lg:max-w-4xl lg:mx-auto xl:max-w-none xl:mx-0">
            {products.map((product) => {
              const price = product?.prices?.find(
                (price) => price.interval === billingInterval
              );
              if (!price) return null;
              const priceString = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: price.currency!,
                minimumFractionDigits: 0
              }).format((price?.unit_amount || 0) / 100);
              return (
                <div
                  key={product.id}
                  className={cn(
                    'flex flex-col rounded-lg shadow-sm divide-y divide-zinc-600 bg-zinc-900',
                    {
                      'border border-pink-500': subscription
                        ? product.name === subscription?.prices?.products?.name
                        : product.name === 'Freelancer'
                    },
                    'flex-1', // This makes the flex item grow to fill the space
                    'basis-1/3', // Assuming you want each card to take up roughly a third of the container's width
                    'max-w-xs' // Sets a maximum width to the cards to prevent them from getting too large
                  )}
                >
                  <div className="p-6">
                    <h2 className="text-2xl font-semibold leading-6 text-white">
                      {product.name}
                    </h2>
                    <p className="mt-4 text-zinc-300">{product.description}</p>
                    <p className="mt-8">
                      <span className="text-5xl font-extrabold white">
                        {priceString}
                      </span>
                      <span className="text-base font-medium text-zinc-100">
                        /{billingInterval}
                      </span>
                    </p>
                    <Button
                      variant="outline"
                      type="button"
                      loading={priceIdLoading === price.id}
                      onClick={() => handleStripeCheckout(price)}
                      className="block w-full py-2 mt-8 text-sm font-semibold text-center text-white rounded-md hover:bg-zinc-900"
                    >
                      {subscription ? 'Manage' : 'Subscribe'}
                    </Button>
                  </div>
                </div>
              );
            })}
          </div> */}
        </div>
      </section>
    );
  }
}