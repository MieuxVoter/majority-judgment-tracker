import React, {Component} from "react";
import Select from 'react-select';
import graphs from "../data/graphs"
import dynamic from 'next/dynamic'

const DynamicPlot = dynamic(import('react-plotly.js'), {
  ssr: false
})


export const getStaticProps = async ({locale}) => {
  const matter = require('gray-matter')
  const {join, parse} = require('path')
  const {readFileSync} = require('fs')
  const glob = require('glob')

  const graphDir = join(process.cwd(), 'data/graphs/')
  const graphs = {}
  glob.sync(join(graphDir, '*.json')).forEach((file) => {
    const key = parse(file).name;
    const [start, end, who] = key.split('_')
    const fileContents = readFileSync(file, 'utf8')
    graphs[`${who.toUpperCase()} - ${start}`] = JSON.parse(fileContents)
  })
  return {
    props: {
      graphs,
    },
  };
};


class App extends Component {

  constructor(props) {
    super()
    this.keys = Object.keys(props.graphs)
    this.options = this.keys.map((opt) => ({label: opt, value: opt}))
    this.defaultValue = this.keys[this.keys.length - 1]
    this.state = {option: this.defaultValue}
  }

  onChange = (
    inputValue,
    {action, prevInputValue}
  ) => {
    switch (action) {
      case 'select-option':
        this.setState({option: inputValue.value});
    }
  };


  render() {
    const {option} = this.state
    console.log(this.defaultValue)

    let plot = null
    if (option) {
      const graph = this.props.graphs[option]
      const {data, layout} = graph;
      plot = (
        <DynamicPlot data={data} layout={layout}
          config={{responsive: true}}
          useResizeHandler={true}
          style={{width: "100%", height: "100%"}}
        />
      )
    }

    return (
      <div>
        <Select
          className="basic-single"
          classNamePrefix="select"
          defaultValue={this.defaultValue}
          isClearable
          onChange={this.onChange}
          name="color"
          options={this.options}
        />

        <div
          style={{
            color: 'hsl(0, 0%, 40%)',
            fontSize: 12,
            fontStyle: 'italic',
            marginTop: '1em',
            width: "100%",
          }}
        >
        </div>
        {plot}
      </div >
    );
  }
}

export default App;
