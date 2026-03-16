import React from "react";

export default function Blog() {
	return (
		<div className="min-h-screen bg-white max-w-4xl mx-auto px-6 py-10">
			<header className="mb-10">
				<h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-gray-900">
					The Hidden Problem in Retail Trading — And Why It Needs AI
				</h1>
			</header>

			<section className="mb-10">
				<p className="text-base sm:text-lg leading-relaxed text-gray-800">
					Retail trading has expanded dramatically in recent years. Mobile trading apps,
					instant account opening, and low brokerage fees have enabled millions of people
					to participate in financial markets.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					But today’s participants are not just professional traders. They include:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>retail traders exploring active trading</li>
					<li>salaried professionals investing part-time</li>
					<li>first-time investors managing savings through markets</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Despite unprecedented access to tools, data, and platforms, a large share of
					retail participants still struggle to achieve consistent results. The explanation
					is often assumed to be simple: people lose money because they choose the wrong
					stocks or strategies.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					However, research on retail investors—especially in India—suggests something
					different. The real issue is <strong>not stock selection.</strong> The real issue
					is <strong>how decisions are executed under pressure.</strong>
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					A Reality Check from Market Data
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Recent regulatory data offers a stark view of retail trading outcomes. A study
					by the <strong>Securities and Exchange Board of India (SEBI)</strong> found that{" "}
					<strong>
						about 91% of individual traders in the equity derivatives market incurred net
						losses in FY2025
					</strong>
					.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					The same analysis shows that retail traders collectively lost{" "}
					<strong>over ₹1 lakh crore in derivatives trading</strong>, with the{" "}
					<strong>average loss around ₹1.1 lakh per trader</strong>.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Over a longer period, the numbers are even more striking. Across three years,{" "}
					<strong>93% of individual traders in equity F&amp;O markets lost money</strong>,
					with cumulative losses exceeding <strong>₹1.8 lakh crore</strong>.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					These statistics point to an important conclusion: the challenge facing retail
					traders is <strong>systemic</strong>, not individual. Millions of participants see
					similar outcomes despite having access to the same tools, charts, and strategies.
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					The Execution Problem in Retail Trading
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					For many Indian retail traders, underperformance is driven less by what they
					trade and more by <strong>how they trade</strong>.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Execution decisions such as:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>when to enter a trade</li>
					<li>when to exit</li>
					<li>how large a position to take</li>
					<li>how often to trade</li>
					<li>whether to follow a stop-loss</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					often have a greater impact on outcomes than the underlying idea behind the
					trade.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Academic research studying Indian investors repeatedly finds that{" "}
					<strong>behavioural biases strongly influence these execution decisions</strong>.
					These biases include:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>
						<strong>Overconfidence</strong>
					</li>
					<li>
						<strong>Herd behaviour</strong>
					</li>
					<li>
						<strong>Loss aversion</strong>
					</li>
					<li>
						<strong>Anchoring</strong>
					</li>
					<li>
						<strong>Fear of Missing Out (FOMO)</strong>
					</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					These are not abstract concepts. They shape <strong>real trading behaviour</strong>
					.
				</p>

				<h3 className="mt-8 text-xl sm:text-2xl font-semibold text-gray-900">Evidence</h3>
				<p className="mt-3 text-base sm:text-lg leading-relaxed text-gray-800">
					<a
						href="https://www.ijfmr.com/papers/2025/6/63780.pdf"
						className="text-blue-600 hover:text-blue-700 underline underline-offset-4 break-words"
					>
						https://www.ijfmr.com/papers/2024/2/impact-of-behavioural-biases-on-investment-decisions-of-retail-investors
					</a>
				</p>
				<p className="mt-3 text-base sm:text-lg leading-relaxed text-gray-800">
					<em>
						This paper studies how psychological biases such as overconfidence and herding
						influence investment decisions of Indian retail investors.
					</em>
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					Where Biases Become Most Powerful
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Behavioural biases become especially powerful in environments where decisions
					must be made quickly. This is why they are most visible in:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>intraday trading</li>
					<li>options trading</li>
					<li>high-frequency speculation</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					These environments create rapid feedback loops. Prices move fast. Traders react
					emotionally. Decisions are made within seconds.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Research examining Indian retail investing notes that{" "}
					<strong>
						real-time market feedback and emotional stress amplify behavioural distortions
					</strong>
					, especially in short-term trading.
				</p>
				<p className="mt-6 text-base sm:text-lg leading-relaxed text-gray-800">Source:</p>
				<p className="mt-3 text-base sm:text-lg leading-relaxed text-gray-800">
					<a
						href="https://iosrjournals.org/iosr-jbm/papers/Vol27-issue10/Ser-7/I2710078193.pdf"
						className="text-blue-600 hover:text-blue-700 underline underline-offset-4 break-words"
					>
						https://www.iosrjournals.org/iosr-jbm/papers/Vol24-issue7/Series-5/A2407050107.pdf
					</a>
				</p>
				<p className="mt-3 text-base sm:text-lg leading-relaxed text-gray-800">
					<em>
						This research explains how behavioural finance effects become stronger in fast
						trading environments such as derivatives and intraday markets.
					</em>
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					How Behavioural Biases Appear in Real Trades
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Behavioural finance research reveals clear patterns in how retail investors
					execute trades. One of the most common patterns is the{" "}
					<strong>disposition effect</strong>.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Because of <strong>loss aversion</strong>, traders tend to:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>sell profitable trades too quickly</li>
					<li>hold losing trades too long</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Over time, this behaviour erodes portfolio returns—even when the original trade
					idea was reasonable.
				</p>
				<p className="mt-6 text-base sm:text-lg leading-relaxed text-gray-800">Source:</p>
				<p className="mt-3 text-base sm:text-lg leading-relaxed text-gray-800">
					<a
						href="https://rsisinternational.org/journals/ijrsi/articles/a-study-on-behavioral-biases-influencing-investment-decisions-among-retail-investors-in-bengaluru-city/"
						className="text-blue-600 hover:text-blue-700 underline underline-offset-4 break-words"
					>
						https://www.rsisinternational.org/journals/ijrsi/articles/a-study-on-behavioural-biases-influencing-investment-decisions
					</a>
				</p>
				<p className="mt-3 text-base sm:text-lg leading-relaxed text-gray-800">
					<em>
						This study identifies loss aversion and overconfidence as major drivers of
						trading behaviour among retail investors.
					</em>
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					Social Signals and Herd Behaviour
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Modern retail trading is also heavily shaped by social signals. Market
					commentary from:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>Telegram groups</li>
					<li>YouTube channels</li>
					<li>influencers and trading communities</li>
					<li>television market discussions</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					can trigger herd behaviour.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					When large numbers of traders respond to the same signals simultaneously, it
					often results in:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>chasing momentum too late</li>
					<li>buying near peaks</li>
					<li>panic selling during corrections</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					In these situations, losses occur not because the asset itself was poor—but
					because the <strong>timing of entry and exit decisions was flawed</strong>.
				</p>
				<p className="mt-6 text-base sm:text-lg leading-relaxed text-gray-800">Source:</p>
				<p className="mt-3 text-base sm:text-lg leading-relaxed text-gray-800">
					<a
						href="https://ijcrt.org/papers/IJCRT2512012.pdf"
						className="text-blue-600 hover:text-blue-700 underline underline-offset-4 break-words"
					>
						https://ijcrt.org/papers/IJCRT2305832.pdf
					</a>
				</p>
				<p className="mt-3 text-base sm:text-lg leading-relaxed text-gray-800">
					<em>
						This research examines herd behaviour and FOMO among retail investors and its
						influence on trading decisions.
					</em>
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					The India-Specific Retail Trading Context
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Retail participation in Indian markets has grown rapidly due to:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>simplified digital KYC processes</li>
					<li>mobile-first brokerage platforms</li>
					<li>social media financial content</li>
					<li>constant exposure to trading signals and tips</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					While this has democratized access to markets, it has also increased exposure to{" "}
					<strong>emotionally driven trading behaviour</strong>.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Research analysing individual investor behaviour in India concludes that
					behavioural biases are{" "}
					<strong>deeply embedded in how retail investors interpret and react to markets</strong>
					.
				</p>
				<p className="mt-6 text-base sm:text-lg leading-relaxed text-gray-800">Source:</p>
				<p className="mt-3 text-base sm:text-lg leading-relaxed text-gray-800">
					<a
						href="https://www.biitm.ac.in/faculty-publications/img/fp/2020/05%20RKM%20GBR%202018.pdf"
						className="text-blue-600 hover:text-blue-700 underline underline-offset-4 break-words"
					>
						https://www.biitm.ac.in/research/behaviour-of-individual-investors-stock-market-trading.pdf
					</a>
				</p>
				<p className="mt-3 text-base sm:text-lg leading-relaxed text-gray-800">
					<em>
						This academic study examines behavioural patterns of individual investors and
						how psychological biases influence trading decisions.
					</em>
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					The Rise of AI-Native Trading Assistants
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					As retail trading has expanded, a new category of tools has begun to emerge:{" "}
					<strong>AI-native trading assistants</strong>.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					These systems aim to help traders interpret large volumes of market data using
					artificial intelligence. Instead of manually scanning charts and indicators,
					traders can receive automated insights about:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>technical indicators</li>
					<li>trend patterns</li>
					<li>potential trading setups</li>
					<li>statistical signals derived from market data</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					This represents an important shift. For the first time, tools traditionally
					available to institutional trading desks—data analysis, pattern recognition, and
					probabilistic modeling—are becoming accessible to retail traders and working
					professionals.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					However, most current solutions still focus primarily on{" "}
					<strong>analysis rather than decision clarity</strong>.
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					Where Current AI Trading Tools Still Fall Short
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					While AI-powered platforms can process market data faster than humans, they
					often introduce a new problem: <strong>insight overload.</strong>
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Many AI trading tools generate:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>multiple signals</li>
					<li>complex dashboards</li>
					<li>indicator summaries</li>
					<li>probabilistic forecasts</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					But the trader is still left with the final challenge:{" "}
					<strong>What should I actually do right now?</strong>
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					In other words, AI tools frequently stop at <strong>analysis</strong>, rather than
					helping traders reach <strong>clear, timely decisions</strong>.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					This creates several gaps.
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					1. Insight Without Decision
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Most AI trading tools produce signals but rarely explain:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>how reliable the signal is</li>
					<li>how multiple indicators interact</li>
					<li>whether the risk is acceptable</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					For many retail traders—especially those trading part-time—interpreting these
					insights still requires experience and time. The result is that users often
					receive <strong>more information, but not more clarity.</strong>
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					2. Too Slow for Real Trading Decisions
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Retail traders often need to make decisions within seconds. Working professionals
					checking the market during a short break cannot analyze multiple dashboards
					before acting.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Yet many AI platforms still require traders to:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>interpret charts</li>
					<li>compare indicators</li>
					<li>manually evaluate risk</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					The decision process remains slow and cognitively demanding.
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					3. Weak Integration of Behavioral Discipline
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					As behavioural finance research shows, the biggest mistakes in trading come from{" "}
					<strong>execution biases</strong>, not just analytical mistakes.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Yet most AI trading tools focus on <strong>market prediction</strong> rather than{" "}
					<strong>decision discipline</strong>. Very few systems address questions such as:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>Is this trade emotionally driven?</li>
					<li>Is the position size too large?</li>
					<li>Is the trader reacting to FOMO or herd behaviour?</li>
					<li>Does the risk justify the potential reward?</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Without addressing these behavioural factors, even strong analytical insights can
					still lead to poor outcomes.
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					The Opportunity for Decision Intelligence
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					The real opportunity in modern trading technology is not simply generating more
					signals. It is <strong>transforming overwhelming information into fast, clear decisions</strong>
					.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					For retail traders and working professionals, the goal is not to analyze markets
					for hours. The goal is to move from <strong>uncertainty to clarity within seconds</strong>
					.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					This is the gap that decision-intelligence systems aim to solve.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Instead of adding another layer of analysis, they focus on:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>filtering meaningful signals from noise</li>
					<li>combining multiple data sources into a single view</li>
					<li>presenting clear, risk-aware decision guidance</li>
					<li>helping traders act quickly and calmly</li>
				</ul>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					Why This Matters
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Retail participation in financial markets is likely to continue growing. But
					unless the <strong>decision problem</strong> is addressed, many participants will
					continue to struggle despite having access to advanced tools.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					The next evolution in trading technology will therefore not simply be{" "}
					<strong>more AI</strong>. It will be{" "}
					<strong>AI that helps humans decide better — and faster.</strong>
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<section className="mb-10">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					The Missing Layer in Trading Platforms
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Most trading platforms today provide three basic components:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>market data</li>
					<li>charting tools</li>
					<li>trade execution infrastructure</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					But one critical layer is missing: <strong>decision intelligence.</strong>
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Retail traders and working professionals are expected to manually interpret
					dozens of indicators, signals, and opinions before making a decision. For someone
					with a full-time job, this process is simply unrealistic.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					What they need instead is <strong>clarity and speed</strong>—the ability to move
					from overwhelming information to a confident decision{" "}
					<strong>within seconds</strong>.
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

						<section className="mb-4">
				<h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">
					Toward Faster, Clearer Trading Decisions
				</h2>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					Artificial intelligence can process vast amounts of market information almost
					instantly. When used effectively, it can help traders:
				</p>
				<ul className="mt-4 list-disc pl-6 space-y-2 text-base sm:text-lg text-gray-800">
					<li>filter meaningful signals from noise</li>
					<li>evaluate risk before entering a trade</li>
					<li>reduce emotional interference</li>
					<li>reach decisions faster and with greater clarity</li>
				</ul>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					The future of retail trading is therefore not simply about more data. It is about{" "}
					<strong>better decisions made faster</strong>.
				</p>
				<p className="mt-4 text-base sm:text-lg leading-relaxed text-gray-800">
					For millions of retail traders and working professionals navigating increasingly
					complex markets, that shift could make all the difference.
				</p>
			</section>

			<hr className="my-10 border-gray-200" />

			<footer className="text-center pb-10">
				<p className="text-gray-600 text-sm sm:text-base">
					Read the Medium article here:
				</p>

				<a
					href="https://medium.com/@anweshh.mohanty/the-hidden-problem-in-retail-trading-and-why-it-needs-ai-99e12bd64089"
					target="_blank"
					rel="noopener noreferrer"
					className="mt-2 inline-block text-blue-600 hover:text-blue-700 underline underline-offset-4 break-words"
				>
					LINK
				</a>
			</footer>
		</div>
	);
}
