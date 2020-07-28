import 'popper.js'
import $ from 'jquery'
import bootstrap from '../../..'

$(() => {
  $('#resultUID').text(bootstrap.Util.getUID('bs'))
  $('[data-toggle="tooltip"]').tooltip()
})
