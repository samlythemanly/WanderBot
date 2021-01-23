import {Container} from 'inversify';
import getDecorators from 'inversify-inject-decorators';

const container = new Container();

export default container;
export const {lazyInject} = getDecorators(container);

