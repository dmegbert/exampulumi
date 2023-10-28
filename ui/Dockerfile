FROM node:21
RUN mkdir "ui"
WORKDIR ui
COPY package.json ./
COPY yarn.lock ./

RUN yarn install --frozen-lockfile
COPY . ./
EXPOSE 3000
CMD yarn start
