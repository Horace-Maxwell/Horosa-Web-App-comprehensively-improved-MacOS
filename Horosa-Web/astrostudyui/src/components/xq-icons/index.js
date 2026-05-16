import React from 'react';

const lineProps = {
	fill: 'none',
	stroke: 'currentColor',
	strokeWidth: 1.8,
	strokeLinecap: 'round',
	strokeLinejoin: 'round',
};

function Svg({children, viewBox = '0 0 24 24', className = '', ...rest}){
	return (
		<svg
			className={`xq-icon ${className}`}
			viewBox={viewBox}
			width="1em"
			height="1em"
			aria-hidden="true"
			focusable="false"
			{...rest}
		>
			{children}
		</svg>
	);
}

const iconMap = {
	navigation: (
		<Svg>
			<path {...lineProps} d="M4 11.4 12 4l8 7.4" />
			<path {...lineProps} d="M6.5 10.2V20h11V10.2" />
			<path {...lineProps} d="M9.5 20v-6h5v6" />
		</Svg>
	),
	note: (
		<Svg>
			<path {...lineProps} d="M5 5.5h14v10.2H9.6L5 19.4z" />
			<path {...lineProps} d="M8.4 9h7.2M8.4 12.2h4.8" />
		</Svg>
	),
	tools: (
		<Svg>
			<path {...lineProps} d="M14.2 5.2a4 4 0 0 0 4.6 4.6L9.2 19.4 5 15.2z" />
			<path {...lineProps} d="m6.7 13.5 3.8 3.8" />
		</Svg>
	),
	newChart: (
		<Svg>
			<circle {...lineProps} cx="12" cy="12" r="8.5" />
			<path {...lineProps} d="M12 8v8M8 12h8" />
		</Svg>
	),
	aiExport: (
		<Svg>
			<path {...lineProps} d="M7 4.5h7l3 3V19.5H7z" />
			<path {...lineProps} d="M14 4.5V8h3" />
			<path {...lineProps} d="M9.4 13.2h5.2M9.4 16h3.7" />
		</Svg>
	),
	aiSettings: (
		<Svg>
			<path {...lineProps} d="M12 3.8v3M12 17.2v3M4.9 7.9l2.6 1.5M16.5 14.6l2.6 1.5M19.1 7.9l-2.6 1.5M7.5 14.6l-2.6 1.5" />
			<circle {...lineProps} cx="12" cy="12" r="3.2" />
		</Svg>
	),
	diagnostics: (
		<Svg>
			<path {...lineProps} d="M7 5.5h10v4.2a5 5 0 0 1 2 4.1c0 3.4-2.8 6.2-7 6.2s-7-2.8-7-6.2a5 5 0 0 1 2-4.1z" />
			<path {...lineProps} d="M9.2 5.5V3.8M14.8 5.5V3.8M8 11.5h8M8.2 15.2h7.6" />
		</Svg>
	),
	search: (
		<Svg>
			<circle {...lineProps} cx="10.5" cy="10.5" r="5.8" />
			<path {...lineProps} d="m15 15 4 4" />
		</Svg>
	),
	theme: (
		<Svg>
			<path {...lineProps} d="M17.8 14.8A7 7 0 0 1 9.2 6.2 7 7 0 1 0 17.8 14.8z" />
			<path {...lineProps} d="M16 4.2v2.2M20.2 8.4H18M18.8 5.6l-1.6 1.6" />
		</Svg>
	),
	locastro: (
		<Svg>
			<path {...lineProps} d="M12 20.2s6-5.1 6-10.1A6 6 0 0 0 6 10.1c0 5 6 10.1 6 10.1z" />
			<circle {...lineProps} cx="12" cy="10.1" r="2.3" />
		</Svg>
	),
	user: (
		<Svg>
			<circle {...lineProps} cx="12" cy="8.6" r="3.3" />
			<path {...lineProps} d="M5.8 20a6.2 6.2 0 0 1 12.4 0" />
		</Svg>
	),
	astro: (
		<Svg>
			<circle {...lineProps} cx="12" cy="12" r="8.6" />
			<path {...lineProps} d="M12 3.4v17.2M3.4 12h17.2M5.9 5.9l12.2 12.2M18.1 5.9 5.9 18.1" opacity=".55" />
			<circle cx="12" cy="12" r="1.6" fill="currentColor" />
		</Svg>
	),
	direction: (
		<Svg>
			<path {...lineProps} d="M4 16.5 9 11l3.3 2.8L19.5 5.5" />
			<path {...lineProps} d="M15.5 5.5h4v4" />
		</Svg>
	),
	bazi: (
		<Svg>
			<rect {...lineProps} x="5" y="5" width="14" height="14" rx="1.2" />
			<path {...lineProps} d="M12 5v14M5 12h14" />
			<path {...lineProps} d="M8.2 8.2h.1M15.7 8.2h.1M8.2 15.8h.1M15.7 15.8h.1" />
		</Svg>
	),
	ziwei: (
		<Svg>
			<circle {...lineProps} cx="12" cy="12" r="7.5" />
			<path {...lineProps} d="M12 4.5v15M4.5 12h15" />
			<path {...lineProps} d="M12 8.2 14.1 12 12 15.8 9.9 12z" />
		</Svg>
	),
	qizheng: (
		<Svg>
			<circle {...lineProps} cx="12" cy="12" r="8.5" />
			<path {...lineProps} d="M12 4.8 14 12l-2 7.2L10 12zM4.8 12H19.2" />
		</Svg>
	),
	vedic: (
		<Svg>
			<rect {...lineProps} x="4" y="4" width="16" height="16" />
			<path {...lineProps} d="M4 12h16M12 4v16M4 4l16 16M20 4 4 20" opacity=".72" />
		</Svg>
	),
	aux: (
		<Svg>
			<path {...lineProps} d="M5 18V9M12 18V5M19 18v-6" />
			<path {...lineProps} d="M4 18h16" />
		</Svg>
	),
	composite: (
		<Svg>
			<circle {...lineProps} cx="9" cy="10" r="4.5" />
			<circle {...lineProps} cx="15" cy="14" r="4.5" />
		</Svg>
	),
	sanshi: (
		<Svg>
			<path {...lineProps} d="M12 3.8 19.1 8v8L12 20.2 4.9 16V8z" />
			<path {...lineProps} d="M12 3.8v16.4M4.9 8 19.1 16M19.1 8 4.9 16" />
		</Svg>
	),
	liureng: (
		<Svg>
			<path {...lineProps} d="M12 4.2 18.8 8v8L12 19.8 5.2 16V8z" />
			<circle {...lineProps} cx="12" cy="12" r="3" />
		</Svg>
	),
	qimen: (
		<Svg>
			<rect {...lineProps} x="4" y="4" width="16" height="16" />
			<path {...lineProps} d="M9.3 4v16M14.7 4v16M4 9.3h16M4 14.7h16" />
		</Svg>
	),
	liuyao: (
		<Svg>
			<path {...lineProps} d="M6 6h12M6 9.2h12M6 12.4h12M6 15.6h12M6 18.8h12" />
		</Svg>
	),
	taiyi: (
		<Svg>
			<circle {...lineProps} cx="12" cy="12" r="7.8" />
			<path {...lineProps} d="M12 4.2v15.6M4.2 12h15.6" />
			<path {...lineProps} d="M8.4 8.4h7.2v7.2H8.4z" />
		</Svg>
	),
	solstice: (
		<Svg>
			<circle {...lineProps} cx="12" cy="12" r="4.2" />
			<path {...lineProps} d="M12 3.8v2M12 18.2v2M3.8 12h2M18.2 12h2M6.2 6.2l1.4 1.4M16.4 16.4l1.4 1.4M17.8 6.2l-1.4 1.4M7.6 16.4l-1.4 1.4" />
		</Svg>
	),
	fengshui: (
		<Svg>
			<circle {...lineProps} cx="12" cy="12" r="8.5" />
			<path {...lineProps} d="M12 6.2a5.8 5.8 0 0 0 0 11.6M12 6.2a2.9 2.9 0 0 1 0 5.8M12 12a2.9 2.9 0 0 0 0 5.8" />
		</Svg>
	),
	other: (
		<Svg>
			<path {...lineProps} d="M6 6h5v5H6zM13 6h5v5h-5zM6 13h5v5H6zM13 13h5v5h-5z" />
		</Svg>
	),
	ai: (
		<Svg>
			<path {...lineProps} d="M12 3.8 13.8 9l5.2 1.8-5.2 1.8L12 17.8l-1.8-5.2L5 10.8 10.2 9z" />
			<path {...lineProps} d="M18 4.5l.7 2.1 2.1.7-2.1.7-.7 2.1-.7-2.1-2.1-.7 2.1-.7z" />
		</Svg>
	),
	threeD: (
		<Svg>
			<path {...lineProps} d="M12 3.8 19 8v8l-7 4.2L5 16V8z" />
			<path {...lineProps} d="M12 12 5 8M12 12l7-4M12 12v8.2" />
		</Svg>
	),
	calendar: (
		<Svg>
			<rect {...lineProps} x="4.5" y="6" width="15" height="13.5" rx="1.5" />
			<path {...lineProps} d="M8 4.5V8M16 4.5V8M4.5 10h15" />
		</Svg>
	),
	support: (
		<Svg>
			<path {...lineProps} d="M5 7.5h14M5 12h14M5 16.5h14" />
			<path {...lineProps} d="M8 5v14M16 5v14" />
		</Svg>
	),
	book: (
		<Svg>
			<path {...lineProps} d="M5 5.5h6.2A2.8 2.8 0 0 1 14 8.3v10.2a2.8 2.8 0 0 0-2.8-2.8H5z" />
			<path {...lineProps} d="M19 5.5h-5a2.8 2.8 0 0 0-2.8 2.8" />
		</Svg>
	),
	live: (
		<Svg>
			<circle {...lineProps} cx="12" cy="12" r="8.5" />
			<path fill="currentColor" d="M10 8.2v7.6l5.8-3.8z" />
		</Svg>
	),
	admin: (
		<Svg>
			<path {...lineProps} d="M12 4.5 18.5 7v5.2c0 4.2-2.6 6.7-6.5 7.8-3.9-1.1-6.5-3.6-6.5-7.8V7z" />
			<path {...lineProps} d="M9.2 12.2 11.2 14l3.8-4" />
		</Svg>
	),
};

export function XQIcon({name, className = '', ...rest}){
	return React.cloneElement(iconMap[name] || iconMap.astro, {
		className: `xq-icon ${className}`.trim(),
		...rest,
	});
}

export default XQIcon;
