import { Form } from 'antd';
import { preventEnterPress } from '../../utils/helper';
import { XQButton, XQInput } from '../xq-ui';
import XQIcon from '../xq-icons';

export default function ChangePwdForm(props){
	const [form] = Form.useForm();
    const { getFieldValue } = form;
    const FormItem = Form.Item;

	function formFieldsChanged(changedFields, allFields){
        if(props.dispatch){
			let values = {
				pwdFields: {
					...props.fields, 
				},
			};
			for(let fld of allFields){
				let key = fld.name[0];
				values.pwdFields[key].value = fld.value;
			}

			
			props.dispatch({
				type: 'user/save',
				payload:{ 
					...values,
				},
			});	
		}
	}

    function handleSubmit(values){
        form.validateFields().then((values)=>{
			if(props.dispatch){
				props.dispatch({
					type: 'user/changePwd',
					payload:{ 
						...values,
					},
				});
			}
		});

	}
	
	return (
		<div>
			<Form onFinish={handleSubmit} onKeyPress={preventEnterPress}
				onFieldsChange={formFieldsChanged}
				fields={props.fieldsAry}
				form={form}
			>
				<FormItem 
					name='oldPwd'
					rules={[{ 
						required: true, 
						message: '请输入您的旧密码！' 
					}]}
				>
					<XQInput prefix={<XQIcon name="lock" style={{ color: 'var(--horosa-muted, rgba(0,0,0,.25))' }} />} type="password" placeholder="旧密码" />
				</FormItem>

                <FormItem
					name='newPwd'
					rules={[{ 
						required: true, 
						message: '请输入您的新密码！' 
					}]}
				>
					<XQInput prefix={<XQIcon name="lock" style={{ color: 'var(--horosa-muted, rgba(0,0,0,.25))' }} />} type="password" placeholder="新密码" />
				</FormItem>

                <FormItem
					name='newPwdAgain'
					rules={[{ 
						required: true, 
						message: '请确认您的新密码！' ,                               
					},{
						validator: (rule, value, callback)=>{
							if (value && value !== getFieldValue('newPwd')) {
								callback('两次输入不一致！');
							}
							callback();
						}
					}]}
				>
					<XQInput prefix={<XQIcon name="lock" style={{ color: 'var(--horosa-muted, rgba(0,0,0,.25))' }} />} type="password" placeholder="新密码确认" />
				</FormItem>

				<FormItem>
					<XQButton type="primary" htmlType="submit">
						提&nbsp;交
					</XQButton>
				</FormItem>


			</Form>
		</div>
	);
    
}
