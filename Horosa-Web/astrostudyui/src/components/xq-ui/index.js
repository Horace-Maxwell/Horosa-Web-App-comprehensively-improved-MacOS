import React from 'react';
import { Button, Card, Drawer, Input, Modal, Radio, Select, Tabs, Tooltip } from 'antd';
import XQIcon from '../xq-icons';

export function XQButton({children, iconName, className = '', variant = 'default', ...rest}){
	const icon = iconName ? <XQIcon name={iconName} /> : rest.icon;
	const visualVariant = variant === 'default' && rest.type === 'primary' ? 'primary' : variant;
	return (
		<Button
			{...rest}
			icon={icon}
			className={`xq-button xq-button-${visualVariant} ${className}`.trim()}
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

export function XQCard({children, className = '', ...rest}){
	return (
		<Card
			{...rest}
			className={`xq-card ${className}`.trim()}
		>
			{children}
		</Card>
	);
}

export function XQToolbar({children, className = '', compact = false, ...rest}){
	return (
		<div {...rest} className={`xq-toolbar ${compact ? 'xq-toolbar-compact' : ''} ${className}`.trim()}>
			{children}
		</div>
	);
}

export function XQSectionTitle({children, className = '', ...rest}){
	return (
		<div {...rest} className={`xq-section-title ${className}`.trim()}>
			{children}
		</div>
	);
}

export function XQCheckItem({checked, children, className = '', compact = false, marker, ...rest}){
	return (
		<button
			type="button"
			{...rest}
			className={`xq-check-item ${checked ? 'xq-check-item-checked' : ''} ${compact ? 'xq-check-item-compact' : ''} ${className}`.trim()}
			aria-pressed={checked}
		>
			<span className="xq-check-box" aria-hidden="true">
				{checked ? '✓' : ''}
			</span>
			<span className="xq-check-content">{children}</span>
			{marker ? <span className="xq-check-marker">{marker}</span> : null}
		</button>
	);
}

export function XQCheckList({children, className = '', columns = 1, ...rest}){
	return (
		<div
			{...rest}
			className={`xq-check-list xq-check-list-${columns} ${className}`.trim()}
		>
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

XQSelect.Option = Select.Option;

export function XQInput({className = '', ...rest}){
	return (
		<Input
			{...rest}
			className={`xq-input ${className}`.trim()}
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

XQTabs.TabPane = Tabs.TabPane;

export function XQModal({className = '', children, ...rest}){
	return (
		<Modal
			{...rest}
			className={`xq-modal ${className}`.trim()}
		>
			{children}
		</Modal>
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
