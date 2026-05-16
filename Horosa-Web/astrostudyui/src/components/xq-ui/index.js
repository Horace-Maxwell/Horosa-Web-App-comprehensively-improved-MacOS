import React from 'react';
import { Button, Drawer, Radio, Select, Tabs, Tooltip } from 'antd';
import XQIcon from '../xq-icons';

export function XQButton({children, iconName, className = '', variant = 'default', ...rest}){
	const icon = iconName ? <XQIcon name={iconName} /> : rest.icon;
	return (
		<Button
			{...rest}
			icon={icon}
			className={`xq-button xq-button-${variant} ${className}`.trim()}
		>
			{children}
		</Button>
	);
}

export function XQIconButton({label, iconName, tooltip, className = '', ...rest}){
	const btn = (
		<Button
			{...rest}
			className={`xq-icon-button ${className}`.trim()}
			icon={<XQIcon name={iconName} />}
			aria-label={label || tooltip || iconName}
		>
			{label ? <span className="xq-icon-button-label">{label}</span> : null}
		</Button>
	);
	return tooltip ? <Tooltip title={tooltip}>{btn}</Tooltip> : btn;
}

export function XQToggle({active, children, iconName, className = '', ...rest}){
	return (
		<XQButton
			{...rest}
			iconName={iconName}
			className={`xq-toggle ${active ? 'xq-toggle-active' : ''} ${className}`.trim()}
			aria-pressed={active}
		>
			{children}
		</XQButton>
	);
}

export function XQSegmented({value, options, onChange, className = '', size = 'small'}){
	return (
		<Radio.Group
			size={size}
			buttonStyle="solid"
			value={value}
			onChange={onChange}
			className={`xq-segmented ${className}`.trim()}
		>
			{(options || []).map((item)=>(
				<Radio.Button key={item.value} value={item.value}>{item.label}</Radio.Button>
			))}
		</Radio.Group>
	);
}

export function XQPanel({children, className = '', tone = 'default', ...rest}){
	return (
		<div {...rest} className={`xq-panel xq-panel-${tone} ${className}`.trim()}>
			{children}
		</div>
	);
}

export function XQToolbar({children, className = '', compact = false, ...rest}){
	return (
		<div {...rest} className={`xq-toolbar ${compact ? 'xq-toolbar-compact' : ''} ${className}`.trim()}>
			{children}
		</div>
	);
}

export function XQSelect({className = '', popupClassName = '', dropdownClassName = '', ...rest}){
	return (
		<Select
			{...rest}
			className={`xq-select ${className}`.trim()}
			popupClassName={`xq-select-popup ${popupClassName || dropdownClassName}`.trim()}
		/>
	);
}

export function XQTabs({className = '', ...rest}){
	return (
		<Tabs
			{...rest}
			className={`xq-tabs ${className}`.trim()}
		/>
	);
}

export function XQDrawer({className = '', children, ...rest}){
	return (
		<Drawer
			{...rest}
			className={`xq-drawer ${className}`.trim()}
		>
			{children}
		</Drawer>
	);
}

export function XQNavItem({item, active, onClick}){
	return (
		<button
			type="button"
			className={`xq-nav-item ${active ? 'xq-nav-item-active' : ''}`}
			onClick={onClick}
			title={item.label}
		>
			<span className="xq-nav-item-icon">
				<XQIcon name={item.icon || 'astro'} />
			</span>
			<span className="xq-nav-item-copy">
				{item.group ? <span className="xq-nav-item-group">{item.group}</span> : null}
				<span className="xq-nav-item-label">{item.label}</span>
			</span>
		</button>
	);
}
