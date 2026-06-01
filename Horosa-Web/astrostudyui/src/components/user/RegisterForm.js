import { Form } from 'antd';
import { preventEnterPress } from '../../utils/helper';
import { EmailRegex } from '../../utils/constants';
import ImgToken from '../comp/ImgToken';
import { XQButton, XQInput } from '../xq-ui';
import XQIcon from '../xq-icons';

export default function RegisterForm(props){
	const [form] = Form.useForm();
    const FormItem = Form.Item;

	function formFieldsChanged(changedFields, allFields){
        if(props.dispatch){
			let values = {
				registerFields: {
					...props.fields, 
				},
			};
			for(let fld of allFields){
				let key = fld.name[0];
				values.registerFields[key].value = fld.value;
			}
			
			props.dispatch({
				type: 'app/save',
				payload:{ 
					...values,
				},
			});	
		}
	}
	
	function handleSubmit(values){
		if(props.dispatch){
			props.dispatch({
				type: 'app/register',
				payload:{ 
					...values,
				},
			});
	
		}
	}

	function getToken(val){
		if(props.dispatch){
			props.dispatch({
				type: 'app/save',
				payload:{
					...val,
				},
			});
		}
	}
	
	return (
		<div>
			<Form onFinish={handleSubmit} onKeyPress={preventEnterPress}
				onFieldsChange={formFieldsChanged}
                fields={props.fieldsAry}
                form={form}
			>
				<FormItem
					name='loginId'
					rules={[{ 
						required: true, 
						pattern: EmailRegex,
						message: '请输入您有效的email' 
					}]}
				>
					<XQInput prefix={<XQIcon name="user" style={{ color: 'var(--horosa-muted, rgba(0,0,0,.25))' }} />} placeholder="有效的email" />
				</FormItem>
				
				<FormItem
					name='pwd'
					rules={[{ 
						required: true, 
						message: '请输入您的密码！' 
					}]}
				>
					<XQInput prefix={<XQIcon name="lock" style={{ color: 'var(--horosa-muted, rgba(0,0,0,.25))' }} />} type="password" placeholder="密码" />
				</FormItem>

				<FormItem
					name='imgToken'
					rules={[{ required: true, message: '请输入验证码！' }]}
				>
					<ImgToken onGetToken={getToken} />
				</FormItem>

				<FormItem>
					<XQButton type="primary" htmlType="submit">
						注&nbsp;册
					</XQButton>
				</FormItem>

			</Form>
		</div>
	);
    
}
